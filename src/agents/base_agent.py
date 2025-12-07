"""Base agent class for Kalah AI agents."""

from abc import ABC, abstractmethod
from src.game.game_state import GameState


class BaseAgent(ABC):
    """Abstract base class for all Kalah agents."""
    
    def __init__(self, name: str = "BaseAgent"):
        """
        Initialize agent.
        
        Args:
            name: Agent name
        """
        self.name = name
    
    @abstractmethod
    def select_move(self, state: GameState) -> int:
        """
        Select a move from the current game state.
        
        Args:
            state: Current game state
            
        Returns:
            Pit index (0 to pits_per_row-1) to move from
        """
        pass
    
    def get_name(self) -> str:
        """Get agent name."""
        return self.name
    
    def reset(self):
        """Reset agent state (for batch simulations)."""
        pass


