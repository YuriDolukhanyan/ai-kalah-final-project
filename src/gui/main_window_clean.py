"""Clean main GUI window for Kalah game."""

import tkinter as tk
from tkinter import ttk
from src.gui.game_view import GameView
from src.gui.config_panel import ConfigPanel
from src.gui.statistics_view import StatisticsView
from src.gui.game_controller import GameController
from src.game.game_state import GameState


class MainWindow:
    """Main application window."""
    
    def __init__(self):
        """Initialize main window."""
        self.root = tk.Tk()
        self.root.title("Kalah Game - AI Project")
        self.root.geometry("1200x700+100+100")  # Add position offset
        
        # Create all widgets
        self._create_widgets()
        
        # Initialize controller
        self.controller = GameController(
            self.game_view, self.statistics_view, self.config_panel
        )
        
        # Initialize board
        self._initialize_board()
    
    def _create_widgets(self):
        """Create all GUI widgets."""
        # Main container
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left frame for game
        left_frame = ttk.Frame(main_container)
        main_container.add(left_frame, weight=3)
        
        # Right frame for config
        right_frame = ttk.Frame(main_container)
        main_container.add(right_frame, weight=1)
        
        # Config panel (create first)
        self.config_panel = ConfigPanel(right_frame)
        
        # Game canvas
        pits_per_row = self.config_panel.get_pits_per_row()
        self.game_view = GameView(left_frame, pits_per_row=pits_per_row)
        
        # Buttons
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(side=tk.BOTTOM, pady=10)
        
        self.single_game_btn = ttk.Button(
            btn_frame, text="Play Single Game", command=self._play_single_game
        )
        self.single_game_btn.pack(side=tk.LEFT, padx=5)
        
        self.batch_btn = ttk.Button(
            btn_frame, text="Run Batch Simulation", command=self._run_batch
        )
        self.batch_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(
            btn_frame, text="Stop", command=self._stop, state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Status
        self.status_label = ttk.Label(left_frame, text="Ready")
        self.status_label.pack(side=tk.BOTTOM, pady=5)
        
        # Progress
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            left_frame, variable=self.progress_var, maximum=100
        )
        self.progress_bar.pack(side=tk.BOTTOM, pady=5, fill=tk.X, padx=20)
        
        # Statistics
        self.statistics_view = StatisticsView(right_frame)
        
        # Bind config changes
        self.config_panel.pits_per_row_var.trace('w', lambda *args: self._update_board_from_config())
        self.config_panel.counters_per_pit_var.trace('w', lambda *args: self._update_board_from_config())
    
    def _initialize_board(self):
        """Initialize board with default game state."""
        pits_per_row = self.config_panel.get_pits_per_row()
        counters_per_pit = self.config_panel.get_counters_per_pit()
        initial_state = GameState(
            pits_per_row=pits_per_row,
            counters_per_pit=counters_per_pit
        )
        self.game_view.update_board(initial_state)
    
    def _update_board_from_config(self):
        """Update board when config changes."""
        if hasattr(self, 'config_panel') and hasattr(self, 'game_view'):
            new_pits_per_row = self.config_panel.get_pits_per_row()
            if new_pits_per_row != self.game_view.pits_per_row:
                self.game_view.set_pits_per_row(new_pits_per_row)
            self._initialize_board()
    
    def _play_single_game(self):
        """Play a single game."""
        self.single_game_btn.config(state=tk.DISABLED)
        self.batch_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Playing game...")
        self.progress_var.set(0)
        
        import threading
        def game_thread():
            self.controller.run_single_game()
            self.root.after(0, self._game_finished)
        
        threading.Thread(target=game_thread, daemon=True).start()
    
    def _run_batch(self):
        """Run batch simulation."""
        self.single_game_btn.config(state=tk.DISABLED)
        self.batch_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        num_games = self.config_panel.get_num_games()
        self.status_label.config(text=f"Running batch ({0}/{num_games})...")
        self.progress_var.set(0)
        
        def progress_callback(completed, total):
            progress = (completed / total) * 100
            self.root.after(0, lambda: self.progress_var.set(progress))
            self.root.after(0, lambda: self.status_label.config(
                text=f"Running batch ({completed}/{total})..."
            ))
        
        self.controller.run_batch_simulation(progress_callback)
        
        def check_finished():
            if not self.controller.is_running:
                self.root.after(0, self._batch_finished)
            else:
                self.root.after(100, check_finished)
        
        check_finished()
    
    def _game_finished(self):
        """Called when game finishes."""
        self.single_game_btn.config(state=tk.NORMAL)
        self.batch_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Game finished!")
        self.progress_var.set(100)
    
    def _batch_finished(self):
        """Called when batch finishes."""
        self.single_game_btn.config(state=tk.NORMAL)
        self.batch_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Batch simulation finished!")
        self.progress_var.set(100)
    
    def _stop(self):
        """Stop current simulation."""
        self.controller.stop()
        self.single_game_btn.config(state=tk.NORMAL)
        self.batch_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Stopped")
    
    def run(self):
        """Start the GUI application."""
        self.root.mainloop()

