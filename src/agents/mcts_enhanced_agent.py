"""Enhanced Monte Carlo Tree Search agent with implicit minimax backups."""

import random
import math
from typing import Optional, Dict
from src.agents.base_agent import BaseAgent
from src.game.game_state import GameState
from src.game.rules import Rules
from src.evaluation.heuristics import Heuristics
from src.utils.constants import PLAYER_SOUTH, PLAYER_NORTH


class MCTSEnhancedNode:
    """Node in enhanced MCTS tree with heuristic evaluations."""
    
    def __init__(self, state: GameState, parent: Optional['MCTSEnhancedNode'] = None, 
                 move: Optional[int] = None):
        self.state = state
        self.parent = parent
        self.move = move
        self.children: Dict[int, 'MCTSEnhancedNode'] = {}
        self.visits = 0
        self.wins = 0.0  # From simulations
        self.heuristic_value = 0.0  # From heuristic evaluations
        self.untried_moves = state.get_legal_moves()
    
    def is_fully_expanded(self) -> bool:
        """Check if all moves have been tried."""
        return len(self.untried_moves) == 0
    
    def is_terminal(self) -> bool:
        """Check if node is terminal."""
        return self.state.is_terminal()
    
    def select_child(self, exploration_constant: float, alpha: float) -> 'MCTSEnhancedNode':
        """
        Select child using UCB1 formula with heuristic mixing.
        
        Args:
            exploration_constant: UCB1 exploration parameter
            alpha: Mixing parameter (0=pure simulation, 1=pure heuristic)
        """
        best_score = float('-inf')
        best_child = None
        
        for move, child in self.children.items():
            if child.visits == 0:
                ucb = float('inf')
            else:
                # Mix simulation results with heuristic evaluation
                simulation_value = child.wins / child.visits
                heuristic_value = child.heuristic_value
                
                # Combine using alpha parameter
                exploitation = (1 - alpha) * simulation_value + alpha * heuristic_value
                
                exploration = exploration_constant * math.sqrt(
                    math.log(self.visits) / child.visits
                )
                ucb = exploitation + exploration
            
            if ucb > best_score:
                best_score = ucb
                best_child = child
        
        return best_child
    
    def expand(self, original_player: int) -> 'MCTSEnhancedNode':
        """Expand node by adding a child with heuristic evaluation."""
        if not self.untried_moves:
            return self
        
        move = self.untried_moves.pop()
        next_state = self.state.apply_move(move)
        child = MCTSEnhancedNode(next_state, parent=self, move=move)
        
        # Compute heuristic value immediately upon creation
        child.heuristic_value = self._evaluate_heuristic(next_state, original_player)
        
        self.children[move] = child
        return child
    
    def _evaluate_heuristic(self, state: GameState, original_player: int) -> float:
        """
        Evaluate position using minimax-style heuristic.
        Normalized to [0, 1] range.
        """
        if state.is_terminal():
            final_board = Rules.finalize_game(state.board.copy())
            winner = Rules.get_winner(final_board)
            if winner == original_player:
                return 1.0
            elif winner == 1 - original_player:
                return 0.0
            else:
                return 0.5
        
        # Use heuristic evaluation
        score = Heuristics.evaluate_position(state, original_player)
        
        # Normalize to [0, 1] range
        # Heuristic scores typically range from -200 to +200
        normalized = (score + 200) / 400
        normalized = max(0.0, min(1.0, normalized))  # Clamp
        
        return normalized
    
    def update(self, simulation_result: float, heuristic_result: float, alpha: float):
        """
        Update node statistics with both simulation and heuristic.
        
        Args:
            simulation_result: Result from random playout (0, 0.5, or 1)
            heuristic_result: Result from heuristic evaluation [0, 1]
            alpha: Mixing parameter for combining values
        """
        self.visits += 1
        self.wins += simulation_result
        
        # Update heuristic value as running average
        if self.visits == 1:
            self.heuristic_value = heuristic_result
        else:
            # Running average of heuristic evaluations
            self.heuristic_value = (
                (self.heuristic_value * (self.visits - 1) + heuristic_result) / self.visits
            )
    
    def backpropagate(self, simulation_result: float, heuristic_result: float, alpha: float):
        """Backpropagate both simulation and heuristic results."""
        self.update(simulation_result, heuristic_result, alpha)
        if self.parent:
            # Invert for opponent
            self.parent.backpropagate(1.0 - simulation_result, 1.0 - heuristic_result, alpha)


class MCTSEnhancedAgent(BaseAgent):
    """
    Enhanced Monte Carlo Tree Search agent using implicit minimax backups.
    
    Based on: "Monte Carlo Tree Search with Heuristic Evaluations using 
    Implicit Minimax Backups" (Lanctot et al., 2014)
    """
    
    def __init__(self, iterations: int = 1000, 
                 exploration_constant: float = math.sqrt(2),
                 alpha: float = 0.5,
                 name: str = "MCTS-Enhanced"):
        """
        Initialize Enhanced MCTS agent.
        
        Args:
            iterations: Number of MCTS iterations per move
            exploration_constant: UCB1 exploration constant
            alpha: Mixing parameter (0=pure simulation, 1=pure heuristic)
                   Research shows 0.1-0.5 works best
            name: Agent name
        """
        super().__init__(name)
        self.iterations = iterations
        self.exploration_constant = exploration_constant
        self.alpha = alpha
    
    def select_move(self, state: GameState) -> int:
        """Select best move using Enhanced MCTS."""
        legal_moves = state.get_legal_moves()
        if not legal_moves:
            raise ValueError("No legal moves available")
        
        if len(legal_moves) == 1:
            return legal_moves[0]
        
        root = MCTSEnhancedNode(state)
        original_player = state.current_player
        
        for _ in range(self.iterations):
            # Selection
            node = self._select(root, original_player)
            
            # Expansion
            if not node.is_terminal():
                node = node.expand(original_player)
            
            # Simulation (random playout)
            simulation_result = self._simulate(node.state, original_player)
            
            # Heuristic evaluation
            heuristic_result = node._evaluate_heuristic(node.state, original_player)
            
            # Backpropagation (with both values)
            node.backpropagate(simulation_result, heuristic_result, self.alpha)
        
        # Select best move based on visit count
        best_move = None
        best_visits = -1
        
        for move, child in root.children.items():
            if child.visits > best_visits:
                best_visits = child.visits
                best_move = move
        
        return best_move if best_move is not None else legal_moves[0]
    
    def _select(self, node: MCTSEnhancedNode, original_player: int) -> MCTSEnhancedNode:
        """Select node using enhanced UCB1 with heuristic mixing."""
        while not node.is_terminal():
            if not node.is_fully_expanded():
                return node.expand(original_player)
            else:
                node = node.select_child(self.exploration_constant, self.alpha)
        return node
    
    def _simulate(self, state: GameState, original_player: int) -> float:
        """
        Simulate random game from state.
        
        Returns:
            1.0 if original_player wins, 0.0 if loses, 0.5 if draw
        """
        current_state = state
        max_moves = 200  # Safety limit
        move_count = 0
        
        while not current_state.is_terminal() and move_count < max_moves:
            legal_moves = current_state.get_legal_moves()
            if not legal_moves:
                break
            
            move = random.choice(legal_moves)
            current_state = current_state.apply_move(move)
            move_count += 1
        
        # Determine winner
        final_board = Rules.finalize_game(current_state.board)
        winner = Rules.get_winner(final_board)
        
        if winner == original_player:
            return 1.0
        elif winner == 1 - original_player:
            return 0.0
        else:
            return 0.5
    
    def reset(self):
        """Reset agent (no state to reset for MCTS)."""
        pass
