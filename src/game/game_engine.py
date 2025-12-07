"""Game engine for running Kalah games."""

from typing import Optional, Callable
from src.game.game_state import GameState
from src.game.rules import Rules
from src.utils.constants import PLAYER_SOUTH, PLAYER_NORTH


class GameEngine:
    """Engine for running Kalah games."""
    
    def __init__(self, pits_per_row: int = 6, counters_per_pit: int = 4):
        """
        Initialize game engine.
        
        Args:
            pits_per_row: Number of pits per row
            counters_per_pit: Initial counters per pit
        """
        self.pits_per_row = pits_per_row
        self.counters_per_pit = counters_per_pit
        self.move_callback: Optional[Callable] = None
    
    def set_move_callback(self, callback: Callable):
        """Set callback function called after each move."""
        self.move_callback = callback
    
    def play_game(self, agent_south, agent_north, verbose: bool = False) -> dict:
        """
        Play a complete game between two agents.
        
        Args:
            agent_south: Agent for South player
            agent_north: Agent for North player
            verbose: Print game progress
            
        Returns:
            Dictionary with game result:
            {
                'winner': 0/1/None,
                'south_score': int,
                'north_score': int,
                'moves': int,
                'move_history': list
            }
        """
        state = GameState(
            pits_per_row=self.pits_per_row,
            counters_per_pit=self.counters_per_pit
        )
        
        agents = [agent_south, agent_north]
        move_count = 0
        max_moves = 500  # Safety limit
        
        if verbose:
            print("Starting game...")
            print(state.board)
        
        while not state.is_terminal() and move_count < max_moves:
            current_agent = agents[state.current_player]
            legal_moves = state.get_legal_moves()
            
            if not legal_moves:
                break
            
            # Agent selects move
            try:
                move = current_agent.select_move(state)
                if move not in legal_moves:
                    # Invalid move, pick first legal
                    move = legal_moves[0]
            except Exception as e:
                if verbose:
                    print(f"Agent error: {e}, using first legal move")
                move = legal_moves[0]
            
            # Apply move
            state = state.apply_move(move)
            move_count += 1
            
            if self.move_callback:
                self.move_callback(state, move)
            
            if verbose and move_count % 10 == 0:
                print(f"Move {move_count}: Player {state.current_player} played {move}")
        
        # Finalize game
        final_board = Rules.finalize_game(state.board)
        winner = Rules.get_winner(final_board)
        
        result = {
            'winner': winner,
            'south_score': final_board.south_kalah,
            'north_score': final_board.north_kalah,
            'moves': move_count,
            'move_history': state.move_history
        }
        
        if verbose:
            print(f"\nGame over after {move_count} moves")
            print(f"South: {result['south_score']}, North: {result['north_score']}")
            if winner is not None:
                print(f"Winner: {'South' if winner == PLAYER_SOUTH else 'North'}")
            else:
                print("Draw!")
        
        return result


