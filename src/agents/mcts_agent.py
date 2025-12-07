"""Monte Carlo Tree Search agent."""

import random
import math
from typing import Optional, Dict
from src.agents.base_agent import BaseAgent
from src.game.game_state import GameState
from src.game.rules import Rules
from src.utils.constants import PLAYER_SOUTH, PLAYER_NORTH


class MCTSNode:
    """Node in MCTS tree."""
    
    def __init__(self, state: GameState, parent: Optional['MCTSNode'] = None, 
                 move: Optional[int] = None):
        self.state = state
        self.parent = parent
        self.move = move  # Move that led to this node
        self.children: Dict[int, 'MCTSNode'] = {}
        self.visits = 0
        self.wins = 0.0
        self.untried_moves = state.get_legal_moves()
    
    def is_fully_expanded(self) -> bool:
        """Check if all moves have been tried."""
        return len(self.untried_moves) == 0
    
    def is_terminal(self) -> bool:
        """Check if node is terminal."""
        return self.state.is_terminal()
    
    def select_child(self, exploration_constant: float = math.sqrt(2)) -> 'MCTSNode':
        """Select child using UCB1 formula."""
        best_score = float('-inf')
        best_child = None
        
        for move, child in self.children.items():
            if child.visits == 0:
                ucb = float('inf')
            else:
                exploitation = child.wins / child.visits
                exploration = exploration_constant * math.sqrt(
                    math.log(self.visits) / child.visits
                )
                ucb = exploitation + exploration
            
            if ucb > best_score:
                best_score = ucb
                best_child = child
        
        return best_child
    
    def expand(self) -> 'MCTSNode':
        """Expand node by adding a child."""
        if not self.untried_moves:
            return self
        
        move = self.untried_moves.pop()
        next_state = self.state.apply_move(move)
        child = MCTSNode(next_state, parent=self, move=move)
        self.children[move] = child
        return child
    
    def update(self, result: float):
        """Update node statistics."""
        self.visits += 1
        self.wins += result
    
    def backpropagate(self, result: float):
        """Backpropagate result up the tree."""
        self.update(result)
        if self.parent:
            self.parent.backpropagate(1.0 - result)  # Invert for opponent


class MCTSAgent(BaseAgent):
    """Monte Carlo Tree Search agent."""
    
    def __init__(self, iterations: int = 500, exploration_constant: float = math.sqrt(2),
                 name: str = "MCTS"):
        """
        Initialize MCTS agent.
        
        Args:
            iterations: Number of MCTS iterations per move
            exploration_constant: UCB1 exploration constant
            name: Agent name
        """
        super().__init__(name)
        self.iterations = iterations
        self.exploration_constant = exploration_constant
    
    def select_move(self, state: GameState) -> int:
        """Select best move using MCTS."""
        legal_moves = state.get_legal_moves()
        if not legal_moves:
            raise ValueError("No legal moves available")
        
        if len(legal_moves) == 1:
            return legal_moves[0]
        
        root = MCTSNode(state)
        
        for _ in range(self.iterations):
            # Selection
            node = self._select(root)
            
            # Expansion
            if not node.is_terminal():
                node = node.expand()
            
            # Simulation
            result = self._simulate(node.state, node.state.current_player)
            
            # Backpropagation
            node.backpropagate(result)
        
        # Select best move (most visited)
        best_move = None
        best_visits = -1
        
        for move, child in root.children.items():
            if child.visits > best_visits:
                best_visits = child.visits
                best_move = move
        
        return best_move if best_move is not None else legal_moves[0]
    
    def _select(self, node: MCTSNode) -> MCTSNode:
        """Select node using UCB1."""
        while not node.is_terminal():
            if not node.is_fully_expanded():
                return node.expand()
            else:
                node = node.select_child(self.exploration_constant)
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


