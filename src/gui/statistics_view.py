"""Statistics display panel."""

import tkinter as tk
from tkinter import ttk
from src.simulation.statistics import Statistics


class StatisticsView:
    """Panel for displaying game statistics."""
    
    def __init__(self, parent):
        """
        Initialize statistics view.
        
        Args:
            parent: Parent widget
        """
        self.frame = ttk.LabelFrame(parent, text="Statistics", padding=10)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Statistics display
        self.stats_text = tk.Text(self.frame, height=15, width=40, wrap=tk.WORD)
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.stats_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.stats_text.config(yscrollcommand=scrollbar.set)
        
        # Clear button
        clear_btn = ttk.Button(self.frame, text="Clear Statistics", command=self.clear)
        clear_btn.pack(pady=5)
        
        self.stats = Statistics()
        self.update_display()
    
    def add_game(self, result: dict):
        """Add a game result and update display."""
        self.stats.add_game(result)
        self.update_display()
    
    def add_batch_results(self, results: list):
        """Add batch results and update display."""
        for result in results:
            self.stats.add_game(result)
        self.update_display()
    
    def update_display(self):
        """Update statistics display."""
        summary = self.stats.get_summary()
        detailed = self.stats.get_detailed_stats()
        
        self.stats_text.delete(1.0, tk.END)
        
        if summary['total_games'] == 0:
            self.stats_text.insert(tk.END, "No games played yet.\n")
            return
        
        text = f"""Game Statistics
{'=' * 40}

Total Games: {summary['total_games']}

Win Rates:
  South: {summary['south_wins']} ({summary['south_win_rate']:.2f}%)
  North: {summary['north_wins']} ({summary['north_win_rate']:.2f}%)
  Draws: {summary['draws']} ({summary['draw_rate']:.2f}%)

Game Length:
  Average: {summary['avg_moves']:.1f} moves
"""
        
        if 'min_moves' in detailed:
            text += f"  Min: {detailed['min_moves']} moves\n"
            text += f"  Max: {detailed['max_moves']} moves\n"
        
        text += f"""
Score Difference:
  Average: {summary['avg_score_diff']:.2f}
"""
        
        if 'min_score_diff' in detailed:
            text += f"  Min: {detailed['min_score_diff']}\n"
            text += f"  Max: {detailed['max_score_diff']}\n"
            text += f"  Median: {detailed['median_score_diff']}\n"
        
        self.stats_text.insert(tk.END, text)
        self.stats_text.see(tk.END)
    
    def clear(self):
        """Clear all statistics."""
        self.stats.reset()
        self.update_display()
    
    def get_statistics(self) -> Statistics:
        """Get statistics object."""
        return self.stats


