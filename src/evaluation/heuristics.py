"""Heuristic evaluation functions for Kalah positions."""

from src.game.game_state import GameState
from src.utils.constants import PLAYER_SOUTH, PLAYER_NORTH
from src.game.rules import Rules


class Heuristics:
    """Heuristic evaluation functions."""

    @staticmethod
    def evaluate_position(state: GameState, player: int) -> float:
        """
        Evaluate a position from a player's perspective.

        Args:
            state: Current game state
            player: Player to evaluate for (0=South, 1=North)

        Returns:
            Evaluation score (positive = good for player)
        """
        board = state.board
        south_score = board.south_kalah
        north_score = board.north_kalah

        # Material difference (stones in Kalah) - Primary factor
        if player == PLAYER_SOUTH:
            material = south_score - north_score
        else:
            material = north_score - south_score

        # Position control - stones in own pits vs opponent pits  
        # This helps guide early game without horizon bias
        position_control = Heuristics._evaluate_position_control(state, player)
        
        # Endgame bonus
        endgame_bonus = Heuristics._evaluate_endgame(state, player)
        
        # Combined evaluation:
        # Material heavily weighted, position control as tiebreaker
        score = 100.0 * material + 0.5 * position_control + endgame_bonus
        
        return score

        return score

    @staticmethod
    def _evaluate_capture_potential(state: GameState, player: int) -> float:
        """Evaluate potential for captures."""
        board = state.board
        potential = 0.0

        if player == PLAYER_SOUTH:
            for i in range(board.pits_per_row):
                if board.pits[i] > 0:
                    # Check if this move could capture
                    target_pit = (i + board.pits[i]) % (2 * board.pits_per_row + 2)
                    if target_pit < board.pits_per_row:  # Lands in own pit
                        opposite = 2 * board.pits_per_row - 1 - target_pit
                        if board.pits[opposite] > 0:
                            potential += board.pits[opposite] + 1
        else:  # North
            for i in range(board.pits_per_row):
                pit_index = board.pits_per_row + i
                if board.pits[pit_index] > 0:
                    target_pit = (pit_index + board.pits[pit_index]) % (2 * board.pits_per_row + 2)
                    if board.pits_per_row <= target_pit < 2 * board.pits_per_row:
                        opposite = board.pits_per_row - 1 - (target_pit - board.pits_per_row)
                        if board.pits[opposite] > 0:
                            potential += board.pits[opposite] + 1

        return potential

    @staticmethod
    def _evaluate_extra_turn_potential(state: GameState, player: int) -> float:
        """Evaluate potential for extra turns."""
        board = state.board
        potential = 0.0

        if player == PLAYER_SOUTH:
            own_kalah = board.pits_per_row
            for i in range(board.pits_per_row):
                if board.pits[i] > 0:
                    # Check if this move ends in Kalah
                    target = (i + board.pits[i]) % (2 * board.pits_per_row + 2)
                    if target == own_kalah:
                        potential += 1.0
        else:  # North
            own_kalah = 2 * board.pits_per_row + 1
            for i in range(board.pits_per_row):
                pit_index = board.pits_per_row + i
                if board.pits[pit_index] > 0:
                    target = (pit_index + board.pits[pit_index]) % (2 * board.pits_per_row + 2)
                    if target == own_kalah:
                        potential += 1.0

        return potential

    @staticmethod
    def _evaluate_mobility(state: GameState, player: int) -> float:
        """Evaluate mobility (number of legal moves for the given player)."""
        legal_moves = Rules.get_legal_moves(state.board, player)
        return float(len(legal_moves))

    @staticmethod
    def _evaluate_position_control(state: GameState, player: int) -> float:
        """Evaluate position control (counters in own row vs opponent)."""
        board = state.board

        if player == PLAYER_SOUTH:
            own_counters = sum(board.pits[:board.pits_per_row])
            opp_counters = sum(board.pits[board.pits_per_row:2*board.pits_per_row])
        else:
            own_counters = sum(board.pits[board.pits_per_row:2*board.pits_per_row])
            opp_counters = sum(board.pits[:board.pits_per_row])

        return own_counters - opp_counters

    @staticmethod
    def _evaluate_endgame(state: GameState, player: int) -> float:
        """Evaluate endgame position."""
        board = state.board
        total_counters = board.get_total_counters()

        # Endgame bonus when few counters remain
        if total_counters < 10:
            if player == PLAYER_SOUTH:
                score_diff = board.south_kalah - board.north_kalah
            else:
                score_diff = board.north_kalah - board.south_kalah

            # Large bonus for winning position
            if score_diff > 0:
                return 50.0 * score_diff
            elif score_diff < 0:
                return -50.0 * abs(score_diff)

        return 0.0


