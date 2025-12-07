"""Game board visualization."""

import tkinter as tk
from typing import Optional
from src.game.game_state import GameState
from src.game.board import Board


class GameView:
    """Visual representation of the Kalah board."""
    
    def __init__(self, parent, pits_per_row: int = 6):
        """
        Initialize game view.
        
        Args:
            parent: Parent widget
            pits_per_row: Number of pits per row
        """
        self.pits_per_row = pits_per_row
        self.canvas = tk.Canvas(parent, width=800, height=400, bg='#8B4513', highlightthickness=0)
        self.canvas.pack(side=tk.TOP, padx=10, pady=10)
        
        self.pit_rects = {}  # Store rectangle IDs for pits
        self.kalah_rects = {}  # Store rectangle IDs for Kalahs
        self.text_ids = {}  # Store text IDs for counter displays
        self.highlighted_pit = None  # Currently highlighted pit ID
        
        self._draw_board()
    
    def _draw_board(self):
        """Draw the initial board layout."""
        self.canvas.delete("all")
        
        # Board dimensions
        pit_width = 80
        pit_height = 100
        kalah_width = 100
        kalah_height = 220
        spacing = 10
        start_x = 120
        start_y = 90
        
        # Draw North Kalah (left side)
        kalah_x = start_x - kalah_width - spacing
        kalah_y = start_y
        self.kalah_rects['north'] = self.canvas.create_oval(
            kalah_x, kalah_y, kalah_x + kalah_width, kalah_y + kalah_height,
            fill='#D2691E', outline='black', width=2
        )
        self.text_ids['north_kalah'] = self.canvas.create_text(
            kalah_x + kalah_width / 2, kalah_y + kalah_height / 2,
            text='0', font=('Arial', 16, 'bold'), fill='white'
        )
        
        # Draw North pits (top row, right to left for counterclockwise)
        for i in range(self.pits_per_row):
            pit_x = start_x + (self.pits_per_row - 1 - i) * (pit_width + spacing)
            pit_y = start_y
            pit_id = f'north_{i}'
            self.pit_rects[pit_id] = self.canvas.create_oval(
                pit_x, pit_y, pit_x + pit_width, pit_y + pit_height,
                fill='#DEB887', outline='black', width=2
            )
            self.text_ids[pit_id] = self.canvas.create_text(
                pit_x + pit_width / 2, pit_y + pit_height / 2,
                text='0', font=('Arial', 12), fill='black'
            )
        
        # Draw South Kalah (right side)
        kalah_x = start_x + self.pits_per_row * (pit_width + spacing)
        kalah_y = start_y
        self.kalah_rects['south'] = self.canvas.create_oval(
            kalah_x, kalah_y, kalah_x + kalah_width, kalah_y + kalah_height,
            fill='#D2691E', outline='black', width=2
        )
        self.text_ids['south_kalah'] = self.canvas.create_text(
            kalah_x + kalah_width / 2, kalah_y + kalah_height / 2,
            text='0', font=('Arial', 16, 'bold'), fill='white'
        )
        
        # Draw South pits (bottom row, left to right)
        for i in range(self.pits_per_row):
            pit_x = start_x + i * (pit_width + spacing)
            pit_y = start_y + pit_height + spacing
            pit_id = f'south_{i}'
            self.pit_rects[pit_id] = self.canvas.create_oval(
                pit_x, pit_y, pit_x + pit_width, pit_y + pit_height,
                fill='#DEB887', outline='black', width=2
            )
            self.text_ids[pit_id] = self.canvas.create_text(
                pit_x + pit_width / 2, pit_y + pit_height / 2,
                text='0', font=('Arial', 12), fill='black'
            )
        
        # Labels
        self.canvas.create_text(
            start_x - kalah_width / 2, kalah_y - 20,
            text='North Kalah', font=('Arial', 10, 'bold'), fill='white'
        )
        self.canvas.create_text(
            start_x + self.pits_per_row * (pit_width + spacing) + kalah_width / 2, 
            kalah_y - 20,
            text='South Kalah', font=('Arial', 10, 'bold'), fill='white'
        )
        self.canvas.create_text(
            start_x + self.pits_per_row * (pit_width + spacing) / 2,
            kalah_y - 20,
            text='North', font=('Arial', 10), fill='white'
        )
        self.canvas.create_text(
            start_x + self.pits_per_row * (pit_width + spacing) / 2,
            kalah_y + pit_height * 2 + spacing + 20,
            text='South', font=('Arial', 10), fill='white'
        )
    
    def highlight_pit(self, player: int, pit_index: int):
        """
        Highlight a specific pit that is about to be played.
        
        Args:
            player: 0 for South, 1 for North
            pit_index: Pit index (0 to pits_per_row-1) relative to player
        """
        # Clear previous highlight first
        self.clear_highlight()
        
        # Highlight the new pit
        if player == 0:  # South
            pit_id = f'south_{pit_index}'
        else:  # North
            pit_id = f'north_{pit_index}'
        
        if pit_id in self.pit_rects:
            self.highlighted_pit = pit_id
            # Highlight with bright yellow/gold color and thicker outline
            self.canvas.itemconfig(self.pit_rects[pit_id], fill='#FFD700', outline='red', width=4)
            self.canvas.update()
    
    def clear_highlight(self):
        """Clear any pit highlight."""
        if self.highlighted_pit and self.highlighted_pit in self.pit_rects:
            pit_id = self.highlighted_pit
            # Restore normal appearance - use default fill color
            # The actual color will be set by update_board based on pit contents
            self.canvas.itemconfig(self.pit_rects[pit_id], outline='black', width=2)
            self.highlighted_pit = None
    
    def update_board(self, state: GameState, highlight_pit_index: int = None):
        """
        Update board display with current game state.
        
        Args:
            state: Current game state
            highlight_pit_index: Optional pit index to highlight (relative to current player)
        """
        try:
            board = state.board
            
            # Clear any previous highlight
            self.clear_highlight()
            
            # Verify board has correct number of pits
            expected_pits = 2 * self.pits_per_row
            if len(board.pits) != expected_pits:
                print(f"Warning: Board has {len(board.pits)} pits but GameView expects {expected_pits}")
                # Redraw board to match current board state
                board_pits_per_row = len(board.pits) // 2
                if board_pits_per_row != self.pits_per_row:
                    self.set_pits_per_row(board_pits_per_row)
            
            # Update South pits
            for i in range(self.pits_per_row):
                pit_id = f'south_{i}'
                if pit_id not in self.text_ids or pit_id not in self.pit_rects:
                    print(f"Error: Pit {pit_id} not found in canvas")
                    continue
                count = board.pits[i]
                self.canvas.itemconfig(self.text_ids[pit_id], text=str(count))
                # Highlight if empty
                if count == 0:
                    self.canvas.itemconfig(self.pit_rects[pit_id], fill='#F5DEB3')
                else:
                    self.canvas.itemconfig(self.pit_rects[pit_id], fill='#DEB887')
            
            # Update North pits (reverse order for display)
            for i in range(self.pits_per_row):
                pit_id = f'north_{i}'
                if pit_id not in self.text_ids or pit_id not in self.pit_rects:
                    print(f"Error: Pit {pit_id} not found in canvas")
                    continue
                count = board.pits[self.pits_per_row + i]
                self.canvas.itemconfig(self.text_ids[pit_id], text=str(count))
                # Highlight if empty
                if count == 0:
                    self.canvas.itemconfig(self.pit_rects[pit_id], fill='#F5DEB3')
                else:
                    self.canvas.itemconfig(self.pit_rects[pit_id], fill='#DEB887')
            
            # Update Kalahs
            if 'south_kalah' in self.text_ids:
                self.canvas.itemconfig(self.text_ids['south_kalah'], text=str(board.south_kalah))
            if 'north_kalah' in self.text_ids:
                self.canvas.itemconfig(self.text_ids['north_kalah'], text=str(board.north_kalah))
            
            # Highlight current player
            if 'south' in self.kalah_rects and 'north' in self.kalah_rects:
                if state.current_player == 0:  # South
                    self.canvas.itemconfig(self.kalah_rects['south'], outline='yellow', width=4)
                    self.canvas.itemconfig(self.kalah_rects['north'], outline='black', width=2)
                else:  # North
                    self.canvas.itemconfig(self.kalah_rects['north'], outline='yellow', width=4)
                    self.canvas.itemconfig(self.kalah_rects['south'], outline='black', width=2)
            
            # Highlight pit if specified
            if highlight_pit_index is not None:
                self.highlight_pit(state.current_player, highlight_pit_index)
            
            self.canvas.update()
        except Exception as e:
            print(f"Error updating board: {e}")
            import traceback
            traceback.print_exc()
    
    def set_pits_per_row(self, pits_per_row: int):
        """Update the number of pits per row and redraw the board."""
        if pits_per_row != self.pits_per_row:
            self.pits_per_row = pits_per_row
            self._draw_board()

