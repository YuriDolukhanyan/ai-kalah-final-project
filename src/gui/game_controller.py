"""Game controller connecting GUI to game engine."""

import threading
from src.game.game_engine import GameEngine
from src.game.game_state import GameState
from src.agents.agent_factory import AgentFactory
from src.simulation.game_runner import GameRunner
from src.simulation.statistics import Statistics


class GameController:
    """Controller for managing game execution from GUI."""
    
    def __init__(self, game_view, statistics_view, config_panel):
        """
        Initialize game controller.
        
        Args:
            game_view: GameView instance
            statistics_view: StatisticsView instance
            config_panel: ConfigPanel instance
        """
        self.game_view = game_view
        self.statistics_view = statistics_view
        self.config_panel = config_panel
        
        self.engine = None
        self.runner = None
        self.current_state = None
        self.is_running = False
        self.batch_thread = None
        
        # Step-by-step mode state
        self.step_mode = False
        self.step_state = None
        self.step_agents = None
        self.step_move_count = 0
        self.step_move_callback = None

    def create_agents(self):
        """Create agents based on configuration."""
        south_type = self.config_panel.get_south_agent_type()
        north_type = self.config_panel.get_north_agent_type()

        south_kwargs = {}
        north_kwargs = {}

        # SOUTH PLAYER CONFIG
        if south_type == "minimax":
            depth = self.config_panel.get_south_minimax_depth()
            south_kwargs["depth"] = depth
            south_kwargs["name"] = f"Minimax South (d={depth})"

        elif south_type == "mcts":
            iters = self.config_panel.get_south_mcts_iterations()
            south_kwargs["iterations"] = iters
            south_kwargs["name"] = f"MCTS South ({iters} iter)"

        # NORTH PLAYER CONFIG
        if north_type == "minimax":
            depth = self.config_panel.get_north_minimax_depth()
            north_kwargs["depth"] = depth
            north_kwargs["name"] = f"Minimax North (d={depth})"

        elif north_type == "mcts":
            iters = self.config_panel.get_north_mcts_iterations()
            north_kwargs["iterations"] = iters
            north_kwargs["name"] = f"MCTS North ({iters} iter)"

        agent_south = AgentFactory.create_agent(south_type, **south_kwargs)
        agent_north = AgentFactory.create_agent(north_type, **north_kwargs)

        return agent_south, agent_north

    def run_single_game(self, step_mode=False):
        """Run a single game."""
        if self.is_running:
            return
        
        self.is_running = True
        self.step_mode = step_mode
        
        # Get configuration
        pits_per_row = self.config_panel.get_pits_per_row()
        counters_per_pit = self.config_panel.get_counters_per_pit()
        
        # Create engine and agents
        self.engine = GameEngine(pits_per_row, counters_per_pit)
        agent_south, agent_north = self.create_agents()
        
        # Set up move callback for visualization
        def move_callback(state, move):
            self.game_view.update_board(state)
            self.current_state = state
        
        def step_move_callback(state, move=None, highlight_move=True):
            """Callback for step mode that can highlight the move."""
            if highlight_move and move is not None:
                # Highlight the pit before showing the result
                self.game_view.highlight_pit(state.current_player, move)
                # Small delay to see the highlight
                import time
                time.sleep(0.3)
            self.game_view.update_board(state)
            self.current_state = state
        
        self.engine.set_move_callback(move_callback)
        self.step_move_callback = step_move_callback
        self.move_callback = move_callback  # Store for exit_step_mode
        
        if step_mode:
            # Initialize game state for step-by-step mode
            from src.game.game_state import GameState
            self.step_state = GameState(
                pits_per_row=pits_per_row,
                counters_per_pit=counters_per_pit
            )
            self.step_agents = [agent_south, agent_north]
            self.step_move_count = 0
            
            # Show initial state
            self.game_view.update_board(self.step_state)
            self.current_state = self.step_state
            
            # Don't run the game automatically - wait for next_move button
            self.is_running = True  # Keep running flag True so we can execute moves
        else:
            # Run game normally
            result = self.engine.play_game(agent_south, agent_north, verbose=False)
            
            # Update statistics
            self.statistics_view.add_game(result)
            
            # Show final state
            if self.current_state:
                self.game_view.update_board(self.current_state)
            
            self.is_running = False
    
    def run_batch_simulation(self, progress_callback=None):
        """Run batch simulation in separate thread."""
        if self.is_running:
            return
        
        def batch_worker():
            self.is_running = True
            
            # Get configuration
            pits_per_row = self.config_panel.get_pits_per_row()
            counters_per_pit = self.config_panel.get_counters_per_pit()
            num_games = self.config_panel.get_num_games()
            
            # Create runner and agents
            self.runner = GameRunner(pits_per_row, counters_per_pit)
            agent_south, agent_north = self.create_agents()
            
            # Progress tracking
            completed = [0]
            
            def progress_cb(game_num, total, result):
                completed[0] = game_num
                if progress_callback:
                    progress_callback(game_num, total)
            
            # Run batch
            results = self.runner.run_batch(
                agent_south, agent_north, num_games, progress_cb
            )
            
            # Update statistics
            self.statistics_view.add_batch_results(results)
            
            if progress_callback:
                progress_callback(num_games, num_games)
            
            self.is_running = False
        
        self.batch_thread = threading.Thread(target=batch_worker, daemon=True)
        self.batch_thread.start()
    
    def execute_next_move(self):
        """
        Execute the next move in step mode.
        
        Returns:
            True if move executed, False if game over
        """
        if not self.step_mode or not self.step_state:
            return False
        
        if self.step_state.is_terminal():
            # Finalize game
            from src.game.rules import Rules
            final_board = Rules.finalize_game(self.step_state.board)
            winner = Rules.get_winner(final_board)
            
            result = {
                'winner': winner,
                'south_score': final_board.south_kalah,
                'north_score': final_board.north_kalah,
                'moves': self.step_move_count,
                'move_history': self.step_state.move_history
            }
            
            # Update statistics
            self.statistics_view.add_game(result)
            
            # Show final state
            if self.step_move_callback:
                self.step_move_callback(self.step_state, None)
            
            self.is_running = False
            return False
        
        legal_moves = self.step_state.get_legal_moves()
        if not legal_moves:
            # No legal moves, finalize game
            from src.game.rules import Rules
            final_board = Rules.finalize_game(self.step_state.board)
            winner = Rules.get_winner(final_board)
            
            result = {
                'winner': winner,
                'south_score': final_board.south_kalah,
                'north_score': final_board.north_kalah,
                'moves': self.step_move_count,
                'move_history': self.step_state.move_history
            }
            
            # Update statistics
            self.statistics_view.add_game(result)
            
            self.is_running = False
            return False
        
        # Get current agent and execute move
        current_player = self.step_state.current_player
        current_agent = self.step_agents[current_player]
        
        try:
            move = current_agent.select_move(self.step_state)
            if move not in legal_moves:
                # Invalid move, pick first legal
                move = legal_moves[0]
        except Exception as e:
            # Agent error, use first legal move
            move = legal_moves[0]
        
        # Highlight the pit that will be played BEFORE applying the move
        self.game_view.highlight_pit(current_player, move)
        # Small delay to see the highlight
        import time
        time.sleep(0.5)
        
        # Apply move
        self.step_state = self.step_state.apply_move(move)
        self.step_move_count += 1
        
        # Update UI via callback (without highlighting again)
        if self.step_move_callback:
            self.step_move_callback(self.step_state, move, highlight_move=False)
        
        return True
    
    def exit_step_mode(self):
        """
        Exit step mode and continue the game automatically.
        
        Returns:
            True if successfully switched to auto mode, False if game already finished
        """
        if not self.step_mode or not self.step_state:
            return False
        
        if self.step_state.is_terminal():
            return False
        
        # Switch to auto mode
        self.step_mode = False
        
        # Continue game from current state using the engine
        def continue_game():
            # Use the engine's play_game but start from current state
            # We'll manually continue the game loop
            max_moves = 500
            move_count = self.step_move_count
            
            while not self.step_state.is_terminal() and move_count < max_moves:
                if not self.is_running:  # Check if stopped
                    break
                    
                legal_moves = self.step_state.get_legal_moves()
                if not legal_moves:
                    break
                
                current_agent = self.step_agents[self.step_state.current_player]
                
                try:
                    move = current_agent.select_move(self.step_state)
                    if move not in legal_moves:
                        move = legal_moves[0]
                except Exception as e:
                    move = legal_moves[0]
                
                # Apply move
                self.step_state = self.step_state.apply_move(move)
                move_count += 1
                
                # Update UI
                if self.move_callback:
                    self.move_callback(self.step_state, move)
                
                # Small delay for visibility
                import time
                time.sleep(0.1)
            
            # Finalize game
            if self.step_state.is_terminal():
                from src.game.rules import Rules
                final_board = Rules.finalize_game(self.step_state.board)
                winner = Rules.get_winner(final_board)
                
                result = {
                    'winner': winner,
                    'south_score': final_board.south_kalah,
                    'north_score': final_board.north_kalah,
                    'moves': move_count,
                    'move_history': self.step_state.move_history
                }
                
                # Update statistics
                self.statistics_view.add_game(result)
                
                # Show final state
                if self.move_callback:
                    self.move_callback(self.step_state, None)
            
            self.is_running = False
        
        # Run continuation in a thread
        import threading
        threading.Thread(target=continue_game, daemon=True).start()
        
        return True
    
    def stop(self):
        """Stop current game/simulation."""
        self.is_running = False
        # Reset step mode state
        if self.step_mode:
            self.step_mode = False
            self.step_state = None
            self.step_agents = None
            self.step_move_count = 0


