"""Game state management."""

from src.game.board import Board
from src.game.rules import Rules
from src.utils.constants import PLAYER_SOUTH, PLAYER_NORTH


class GameState:
    """Represents a game state in Kalah."""
    
    def __init__(self, board: Board = None, current_player: int = PLAYER_SOUTH, 
                 pits_per_row: int = 6, counters_per_pit: int = 4):
        """
        Initialize game state.
        
        Args:
            board: Board instance (creates new if None)
            current_player: Current player (0=South, 1=North)
            pits_per_row: Number of pits per row
            counters_per_pit: Initial counters per pit
        """
        if board is None:
            self.board = Board(pits_per_row, counters_per_pit)
        else:
            self.board = board
        self.current_player = current_player
        self.move_history = []
    
    def copy(self) -> 'GameState':
        """Create a deep copy of the game state."""
        new_state = GameState(
            board=self.board.copy(),
            current_player=self.current_player
        )
        new_state.move_history = self.move_history.copy()
        return new_state
    
    def get_legal_moves(self) -> list:
        """Get all legal moves for current player."""
        return Rules.get_legal_moves(self.board, self.current_player)
    
    def apply_move(self, pit_index: int) -> 'GameState':
        """
        Apply a move and return new game state.
        
        Args:
            pit_index: Index of pit to move from
            
        Returns:
            New GameState after move
        """
        new_board, move_type, next_player = Rules.apply_move(
            self.board, self.current_player, pit_index
        )
        
        new_state = GameState(board=new_board, current_player=next_player)
        new_state.move_history = self.move_history + [(self.current_player, pit_index, move_type)]
        
        return new_state
    
    def is_terminal(self) -> bool:
        """Check if game is over."""
        return Rules.is_game_over(self.board)
    
    def get_winner(self) -> int:
        """
        Get winner of the game.
        
        Returns:
            0 for South, 1 for North, None for draw
        """
        return Rules.get_winner(self.board)
    
    def get_scores(self) -> tuple:
        """Get current scores (South, North)."""
        return (self.board.south_kalah, self.board.north_kalah)
    
    def __str__(self) -> str:
        """String representation."""
        return f"Player: {self.current_player}\n{self.board}"


