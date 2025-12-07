"""Statistics collection and analysis."""

from typing import List, Dict
from collections import defaultdict
from src.utils.constants import PLAYER_SOUTH, PLAYER_NORTH


class Statistics:
    """Collects and analyzes game statistics."""
    
    def __init__(self):
        """Initialize statistics collector."""
        self.reset()
    
    def reset(self):
        """Reset all statistics."""
        self.games = []
        self.south_wins = 0
        self.north_wins = 0
        self.draws = 0
        self.total_moves = 0
        self.score_differences = []
    
    def add_game(self, result: Dict):
        """
        Add a game result.
        
        Args:
            result: Game result dictionary
        """
        self.games.append(result)
        
        winner = result.get('winner')
        if winner == PLAYER_SOUTH:
            self.south_wins += 1
        elif winner == PLAYER_NORTH:
            self.north_wins += 1
        else:
            self.draws += 1
        
        self.total_moves += result.get('moves', 0)
        
        south_score = result.get('south_score', 0)
        north_score = result.get('north_score', 0)
        self.score_differences.append(south_score - north_score)
    
    def get_summary(self) -> Dict:
        """
        Get statistics summary.
        
        Returns:
            Dictionary with statistics
        """
        total_games = len(self.games)
        if total_games == 0:
            return {
                'total_games': 0,
                'south_wins': 0,
                'north_wins': 0,
                'draws': 0,
                'south_win_rate': 0.0,
                'north_win_rate': 0.0,
                'draw_rate': 0.0,
                'avg_moves': 0.0,
                'avg_score_diff': 0.0
            }
        
        return {
            'total_games': total_games,
            'south_wins': self.south_wins,
            'north_wins': self.north_wins,
            'draws': self.draws,
            'south_win_rate': self.south_wins / total_games * 100.0,
            'north_win_rate': self.north_wins / total_games * 100.0,
            'draw_rate': self.draws / total_games * 100.0,
            'avg_moves': self.total_moves / total_games,
            'avg_score_diff': sum(self.score_differences) / total_games
        }
    
    def get_detailed_stats(self) -> Dict:
        """Get detailed statistics."""
        summary = self.get_summary()
        
        if len(self.score_differences) == 0:
            return summary
        
        sorted_diffs = sorted(self.score_differences)
        n = len(sorted_diffs)
        
        return {
            **summary,
            'min_score_diff': min(self.score_differences),
            'max_score_diff': max(self.score_differences),
            'median_score_diff': sorted_diffs[n // 2] if n > 0 else 0,
            'min_moves': min(g.get('moves', 0) for g in self.games) if self.games else 0,
            'max_moves': max(g.get('moves', 0) for g in self.games) if self.games else 0,
        }


