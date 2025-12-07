"""Minimax agent with alpha-beta pruning."""

from typing import Tuple
from src.agents.base_agent import BaseAgent
from src.game.game_state import GameState
from src.evaluation.heuristics import Heuristics
from src.utils.constants import PLAYER_SOUTH, PLAYER_NORTH
from src.game.rules import Rules  # <-- NEW: for consistent terminal scoring


class MinimaxAgent(BaseAgent):
    """Minimax agent with alpha-beta pruning."""

    def __init__(self, depth: int = 4, name: str = "Minimax"):
        super().__init__(name)
        self.depth = depth

    def select_move(self, state: GameState) -> int:
        """Select the best move for the current player."""
        legal_moves = state.get_legal_moves()
        if not legal_moves:
            raise ValueError("No legal moves available")

        if len(legal_moves) == 1:
            return legal_moves[0]

        original_player = state.current_player

        # --- Alpha-beta search over moves (no pre-ordering) ---
        best_move = legal_moves[0]
        best_value = float('-inf')
        alpha = float('-inf')
        beta = float('inf')

        for move in legal_moves:
            next_state = state.apply_move(move)
            value = self._minimax(
                next_state,
                self.depth - 1,
                alpha,
                beta,
                original_player,
            )

            if value > best_value:
                best_value = value
                best_move = move

            alpha = max(alpha, best_value)
            if alpha >= beta:
                break  # Alpha-beta cutoff

        return best_move

    def _minimax(
        self,
        state: GameState,
        depth: int,
        alpha: float,
        beta: float,
        original_player: int,
    ) -> float:
        """
        Minimax with alpha-beta pruning.
        `original_player` is the root player whose perspective we are optimizing for.
        """

        # --- Terminal or depth limit: evaluate ---
        if state.is_terminal() or depth == 0:
            return self._evaluate(state, original_player)

        legal_moves = state.get_legal_moves()
        if not legal_moves:
            return self._evaluate(state, original_player)

        # Whose turn is this node for, relative to root player?
        maximizing = (state.current_player == original_player)

        if maximizing:
            value = float('-inf')
            for move in legal_moves:
                next_state = state.apply_move(move)
                eval_score = self._minimax(
                    next_state,
                    depth - 1,
                    alpha,
                    beta,
                    original_player,
                )
                value = max(value, eval_score)
                alpha = max(alpha, value)
                if alpha >= beta:
                    break  # Cutoff
            return value
        else:
            value = float('inf')
            for move in legal_moves:
                next_state = state.apply_move(move)
                eval_score = self._minimax(
                    next_state,
                    depth - 1,
                    alpha,
                    beta,
                    original_player,
                )
                value = min(value, eval_score)
                beta = min(beta, value)
                if alpha >= beta:
                    break  # Cutoff
            return value

    def _evaluate(self, state: GameState, original_player: int) -> float:
        """
        Unified evaluation:
        - If game is over: use **final score difference** (consistent with GameEngine).
        - Otherwise: use heuristic evaluation from original_player's perspective.
        """
        if state.is_terminal():
            # IMPORTANT: finalize board like GameEngine does
            final_board = Rules.finalize_game(state.board.copy())
            south_score = final_board.south_kalah
            north_score = final_board.north_kalah

            diff = south_score - north_score  # South - North
            if original_player == PLAYER_SOUTH:
                return float(diff)
            else:
                return float(-diff)

        # Non-terminal: use your heuristic
        return Heuristics.evaluate_position(state, original_player)
