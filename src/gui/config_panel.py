"""Configuration panel for algorithm selection and game settings."""

import tkinter as tk
from tkinter import ttk
from src.agents.agent_factory import AgentFactory


class ConfigPanel:
    def __init__(self, parent):

        self.frame = ttk.LabelFrame(parent, text="Game Configuration", padding=10)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # SOUTH PLAYER TYPE
        ttk.Label(self.frame, text="South Player:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.south_agent_var = tk.StringVar(value="minimax")
        self.south_agent_combo = ttk.Combobox(
            self.frame, textvariable=self.south_agent_var,
            values=AgentFactory.get_available_agents(), state="readonly", width=15
        )
        self.south_agent_combo.grid(row=0, column=1, padx=5, pady=5)

        # NORTH PLAYER TYPE
        ttk.Label(self.frame, text="North Player:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.north_agent_var = tk.StringVar(value="mcts")
        self.north_agent_combo = ttk.Combobox(
            self.frame, textvariable=self.north_agent_var,
            values=AgentFactory.get_available_agents(), state="readonly", width=15
        )
        self.north_agent_combo.grid(row=1, column=1, padx=5, pady=5)

        # ───────────────────────────────────────────
        # ALGORITHM PARAMETERS (NEW: 4 separate fields)
        # ───────────────────────────────────────────
        self.params_frame = ttk.LabelFrame(self.frame, text="Algorithm Parameters", padding=5)
        self.params_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W+tk.E, pady=5)

        # SOUTH MINIMAX DEPTH
        ttk.Label(self.params_frame, text="South Minimax Depth:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.south_minimax_depth_var = tk.IntVar(value=4)
        ttk.Spinbox(self.params_frame, from_=1, to=12, textvariable=self.south_minimax_depth_var, width=10)\
            .grid(row=0, column=1, padx=5, pady=2)

        # NORTH MINIMAX DEPTH
        ttk.Label(self.params_frame, text="North Minimax Depth:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.north_minimax_depth_var = tk.IntVar(value=4)
        ttk.Spinbox(self.params_frame, from_=1, to=12, textvariable=self.north_minimax_depth_var, width=10)\
            .grid(row=1, column=1, padx=5, pady=2)

        # SOUTH MCTS ITERATIONS
        ttk.Label(self.params_frame, text="South MCTS Iterations:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.south_mcts_iterations_var = tk.IntVar(value=500)
        ttk.Spinbox(self.params_frame, from_=100, to=5000, increment=100,
                    textvariable=self.south_mcts_iterations_var, width=10)\
            .grid(row=2, column=1, padx=5, pady=2)

        # NORTH MCTS ITERATIONS
        ttk.Label(self.params_frame, text="North MCTS Iterations:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.north_mcts_iterations_var = tk.IntVar(value=500)
        ttk.Spinbox(self.params_frame, from_=100, to=5000, increment=100,
                    textvariable=self.north_mcts_iterations_var, width=10)\
            .grid(row=3, column=1, padx=5, pady=2)

        # Game settings
        game_frame = ttk.LabelFrame(self.frame, text="Game Settings", padding=5)
        game_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W+tk.E, pady=5)

        ttk.Label(game_frame, text="Pits per Row:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.pits_per_row_var = tk.IntVar(value=6)
        pits_spin = ttk.Spinbox(
            game_frame, from_=3, to=10, textvariable=self.pits_per_row_var, width=10
        )
        pits_spin.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(game_frame, text="Counters per Pit:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.counters_per_pit_var = tk.IntVar(value=4)
        counters_spin = ttk.Spinbox(
            game_frame, from_=1, to=10, textvariable=self.counters_per_pit_var, width=10
        )
        counters_spin.grid(row=1, column=1, padx=5, pady=2)

        # Batch simulation settings
        batch_frame = ttk.LabelFrame(self.frame, text="Batch Simulation", padding=5)
        batch_frame.grid(row=4, column=0, columnspan=2, sticky=tk.W+tk.E, pady=5)

        ttk.Label(batch_frame, text="Number of Games:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.num_games_var = tk.IntVar(value=1000)
        num_games_spin = ttk.Spinbox(
            batch_frame, from_=1, to=10000, increment=100,
            textvariable=self.num_games_var, width=10
        )
        num_games_spin.grid(row=0, column=1, padx=5, pady=2)

    def get_south_minimax_depth(self): return self.south_minimax_depth_var.get()
    def get_north_minimax_depth(self): return self.north_minimax_depth_var.get()
    def get_south_mcts_iterations(self): return self.south_mcts_iterations_var.get()
    def get_north_mcts_iterations(self): return self.north_mcts_iterations_var.get()

    def get_south_agent_type(self) -> str:
        """Get selected South agent type."""
        return self.south_agent_var.get()

    def get_north_agent_type(self) -> str:
        """Get selected North agent type."""
        return self.north_agent_var.get()

    def get_minimax_depth(self) -> int:
        """Get minimax depth setting."""
        return self.minimax_depth_var.get()

    def get_mcts_iterations(self) -> int:
        """Get MCTS iterations setting."""
        return self.mcts_iterations_var.get()

    def get_pits_per_row(self) -> int:
        """Get pits per row setting."""
        return self.pits_per_row_var.get()

    def get_counters_per_pit(self) -> int:
        """Get counters per pit setting."""
        return self.counters_per_pit_var.get()

    def get_num_games(self) -> int:
        """Get number of games for batch simulation."""
        return self.num_games_var.get()

