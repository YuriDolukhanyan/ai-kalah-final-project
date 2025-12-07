"""Main GUI window for Kalah game."""

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
        print("MainWindow init starting...")
        self.root = tk.Tk()
        self.root.title("Kalah Game - AI Project")
        self.root.geometry("1200x700")
        self.root.configure(bg='gray')
        
        # Configure grid weights for responsive layout
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=3)  # Left panel gets more space
        self.root.grid_columnconfigure(1, weight=1)  # Right panel
        
        # Create main layout
        print("Creating layout...")
        self._create_layout()
        print("Layout created")
        
        # Initialize controller
        print("Creating controller...")
        self.controller = GameController(
            self.game_view, self.statistics_view, self.config_panel
        )
        print("Controller created")
        
        # Initialize board with default state
        print("Initializing board...")
        self._initialize_board()
        print("Board initialized")
        
        print("MainWindow init complete")
    
    def _create_layout(self):
        """Create GUI layout."""
        try:
            # Left panel: Game board and controls (using grid instead of pack)
            left_panel = tk.Frame(self.root, bg='lightyellow', relief=tk.RAISED, borderwidth=2)
            left_panel.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
            
            # Right panel: Configuration and statistics
            right_panel = tk.Frame(self.root, bg='lightblue', relief=tk.RAISED, borderwidth=2)
            right_panel.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
            
            # Configuration panel (create first to get default pits_per_row)
            print("Creating ConfigPanel...")
            self.config_panel = ConfigPanel(right_panel)
            print("ConfigPanel created")
            
            # Game view (now we can use pits_per_row from config_panel)
            pits_per_row = self.config_panel.get_pits_per_row()
            print(f"Creating GameView with pits_per_row={pits_per_row}...")
            self.game_view = GameView(left_panel, pits_per_row=pits_per_row)
            print("GameView created")
            
            # Control buttons
            print("Creating buttons...")
            button_frame = tk.Frame(left_panel, bg='lightgreen', relief=tk.RAISED, borderwidth=2)
            button_frame.pack(side=tk.BOTTOM, pady=10, fill=tk.X)
            
            self.single_game_btn = ttk.Button(
                button_frame, text="Play Single Game", command=self._play_single_game
            )
            self.single_game_btn.pack(side=tk.LEFT, padx=5, pady=5)
            
            self.batch_btn = ttk.Button(
                button_frame, text="Run Batch Simulation", command=self._run_batch
            )
            self.batch_btn.pack(side=tk.LEFT, padx=5, pady=5)
            
            self.stop_btn = ttk.Button(
                button_frame, text="Stop", command=self._stop, state=tk.DISABLED
            )
            self.stop_btn.pack(side=tk.LEFT, padx=5, pady=5)
            print("Buttons created")
            
            # Status label
            self.status_label = ttk.Label(left_panel, text="Ready - TEST", font=('Arial', 14), background='yellow')
            self.status_label.pack(side=tk.BOTTOM, pady=5)
            
            # Progress bar (for batch simulations)
            self.progress_var = tk.DoubleVar()
            self.progress_bar = ttk.Progressbar(
                left_panel, variable=self.progress_var, maximum=100, length=400
            )
            self.progress_bar.pack(side=tk.BOTTOM, pady=5)
            
            # Statistics panel
            print("Creating StatisticsView...")
            self.statistics_view = StatisticsView(right_panel)
            print("StatisticsView created")
            
            # Bind config changes to update board
            self.config_panel.pits_per_row_var.trace('w', lambda *args: self._update_board_from_config())
            self.config_panel.counters_per_pit_var.trace('w', lambda *args: self._update_board_from_config())
        except Exception as e:
            print(f"Error creating layout: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _initialize_board(self):
        """Initialize board with default game state."""
        try:
            pits_per_row = self.config_panel.get_pits_per_row()
            counters_per_pit = self.config_panel.get_counters_per_pit()
            initial_state = GameState(
                pits_per_row=pits_per_row,
                counters_per_pit=counters_per_pit
            )
            self.game_view.update_board(initial_state)
        except Exception as e:
            print(f"Error initializing board: {e}")
            import traceback
            traceback.print_exc()
    
    def _update_board_from_config(self):
        """Update board view when configuration changes."""
        if hasattr(self, 'config_panel') and hasattr(self, 'game_view'):
            # Check if pits_per_row changed
            new_pits_per_row = self.config_panel.get_pits_per_row()
            if new_pits_per_row != self.game_view.pits_per_row:
                # Redraw board with new pits_per_row
                self.game_view.set_pits_per_row(new_pits_per_row)
            # Update board with current state
            self._initialize_board()
    
    def _play_single_game(self):
        """Play a single game."""
        self.single_game_btn.config(state=tk.DISABLED)
        self.batch_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Playing game...")
        self.progress_var.set(0)
        
        # Run in separate thread to avoid blocking GUI
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
        self.status_label.config(text=f"Running batch simulation (0/{num_games})...")
        self.progress_var.set(0)
        
        def progress_callback(completed, total):
            progress = (completed / total) * 100
            self.root.after(0, lambda: self.progress_var.set(progress))
            self.root.after(0, lambda: self.status_label.config(
                text=f"Running batch simulation ({completed}/{total})..."
            ))
        
        def finished_callback():
            self._batch_finished()
        
        self.controller.run_batch_simulation(progress_callback)
        
        # Check when batch is finished
        def check_finished():
            if not self.controller.is_running:
                self.root.after(0, finished_callback)
            else:
                self.root.after(100, check_finished)
        
        check_finished()
    
    def _game_finished(self):
        """Called when single game finishes."""
        self.single_game_btn.config(state=tk.NORMAL)
        self.batch_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Game finished!")
        self.progress_var.set(100)
    
    def _batch_finished(self):
        """Called when batch simulation finishes."""
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

