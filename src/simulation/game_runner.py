"""Game runner for single and batch simulations."""

from typing import List, Dict, Optional, Callable
from src.game.game_engine import GameEngine
from src.agents.base_agent import BaseAgent
from src.utils.constants import PLAYER_SOUTH, PLAYER_NORTH


class GameRunner:
    """Runs single or batch Kalah games."""
    
    def __init__(self, pits_per_row: int = 6, counters_per_pit: int = 4):
        """
        Initialize game runner.
        
        Args:
            pits_per_row: Number of pits per row
            counters_per_pit: Initial counters per pit
        """
        self.engine = GameEngine(pits_per_row, counters_per_pit)
        self.pits_per_row = pits_per_row
        self.counters_per_pit = counters_per_pit
    
    def run_single_game(self, agent_south: BaseAgent, agent_north: BaseAgent,
                       verbose: bool = False) -> Dict:
        """
        Run a single game.
        
        Args:
            agent_south: South player agent
            agent_north: North player agent
            verbose: Print game progress
            
        Returns:
            Game result dictionary
        """
        agent_south.reset()
        agent_north.reset()
        return self.engine.play_game(agent_south, agent_north, verbose)
    
    def run_batch(self, agent_south: BaseAgent, agent_north: BaseAgent,
                  num_games: int = 1000, progress_callback: Optional[Callable] = None) -> List[Dict]:
        """
        Run multiple games and collect results.
        
        Args:
            agent_south: South player agent
            agent_north: North player agent
            num_games: Number of games to play
            progress_callback: Optional callback(completed, total, result)
            
        Returns:
            List of game result dictionaries
        """
        results = []
        
        for i in range(num_games):
            result = self.run_single_game(agent_south, agent_north, verbose=False)
            results.append(result)
            
            if progress_callback:
                progress_callback(i + 1, num_games, result)
        
        return results


