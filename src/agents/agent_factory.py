"""Factory for creating agents."""

from src.agents.base_agent import BaseAgent
from src.agents.random_agent import RandomAgent
from src.agents.minimax_agent import MinimaxAgent
from src.agents.mcts_agent import MCTSAgent


class AgentFactory:
    """Factory for creating agent instances."""
    
    AGENT_TYPES = {
        'random': RandomAgent,
        'minimax': MinimaxAgent,
        'mcts': MCTSAgent,
    }
    
    @staticmethod
    def create_agent(agent_type: str, **kwargs) -> BaseAgent:
        """
        Create an agent instance.
        
        Args:
            agent_type: Type of agent ('random', 'minimax', 'mcts')
            **kwargs: Agent-specific parameters
            
        Returns:
            Agent instance
        """
        if agent_type not in AgentFactory.AGENT_TYPES:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        agent_class = AgentFactory.AGENT_TYPES[agent_type]
        return agent_class(**kwargs)
    
    @staticmethod
    def get_available_agents() -> list:
        """Get list of available agent types."""
        return list(AgentFactory.AGENT_TYPES.keys())


