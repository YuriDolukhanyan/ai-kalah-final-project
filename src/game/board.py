"""Board representation for Kalah game."""

from typing import List
from copy import deepcopy


class Board:
    """Represents the Kalah game board."""
    
    def __init__(self, pits_per_row: int = 6, counters_per_pit: int = 4):
        """
        Initialize the board.
        
        Args:
            pits_per_row: Number of pits in each row (default 6)
            counters_per_pit: Initial counters in each pit (default 4)
        """
        self.pits_per_row = pits_per_row
        self.counters_per_pit = counters_per_pit
        
        # Board layout: [South pits, South Kalah, North pits, North Kalah]
        # South pits: indices 0 to pits_per_row-1
        # South Kalah: index pits_per_row
        # North pits: indices pits_per_row+1 to 2*pits_per_row
        # North Kalah: index 2*pits_per_row+1
        
        self.pits = [counters_per_pit] * (2 * pits_per_row)  # Regular pits
        self.south_kalah = 0
        self.north_kalah = 0
    
    def copy(self) -> 'Board':
        """Create a deep copy of the board."""
        new_board = Board(self.pits_per_row, 0)
        new_board.pits = self.pits.copy()
        new_board.south_kalah = self.south_kalah
        new_board.north_kalah = self.north_kalah
        return new_board
    
    def get_south_pits(self) -> List[int]:
        """Get counters in South player's pits."""
        return self.pits[:self.pits_per_row]
    
    def get_north_pits(self) -> List[int]:
        """Get counters in North player's pits."""
        return self.pits[self.pits_per_row:]
    
    def get_pit(self, player: int, pit_index: int) -> int:
        """
        Get counter count in a specific pit.
        
        Args:
            player: 0 for South, 1 for North
            pit_index: Index of pit (0 to pits_per_row-1)
        """
        if player == 0:  # South
            return self.pits[pit_index]
        else:  # North
            return self.pits[self.pits_per_row + pit_index]
    
    def get_kalah(self, player: int) -> int:
        """Get counter count in player's Kalah."""
        if player == 0:  # South
            return self.south_kalah
        else:  # North
            return self.north_kalah
    
    def is_empty_row(self, player: int) -> bool:
        """Check if player's row is empty."""
        if player == 0:  # South
            return all(count == 0 for count in self.pits[:self.pits_per_row])
        else:  # North
            return all(count == 0 for count in self.pits[self.pits_per_row:])
    
    def get_total_counters(self) -> int:
        """Get total counters on board (excluding Kalahs)."""
        return sum(self.pits)
    
    def __str__(self) -> str:
        """String representation of the board."""
        north_pits = self.get_north_pits()
        south_pits = self.get_south_pits()
        
        # Reverse north pits for display (counterclockwise)
        north_display = list(reversed(north_pits))
        
        lines = [
            f"North Kalah: {self.north_kalah}",
            f"North: {north_display}",
            f"South: {south_pits}",
            f"South Kalah: {self.south_kalah}"
        ]
        return "\n".join(lines)


