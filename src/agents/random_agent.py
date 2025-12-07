"""Random agent for baseline comparison."""

import random
from src.agents.base_agent import BaseAgent
from src.game.game_state import GameState


class RandomAgent(BaseAgent):
    """Agent that selects random legal moves."""
    
    def __init__(self):
        """Initialize random agent."""
        super().__init__("Random")
    
    def select_move(self, state: GameState) -> int:
        """Select a random legal move."""
        legal_moves = state.get_legal_moves()
        if not legal_moves:
            raise ValueError("No legal moves available")
        return random.choice(legal_moves)


