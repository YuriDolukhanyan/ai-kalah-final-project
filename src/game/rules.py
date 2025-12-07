"""Game rules and move execution logic."""

from typing import Tuple, Optional, List
from src.game.board import Board
from src.utils.constants import PLAYER_SOUTH, PLAYER_NORTH, MOVE_NORMAL, MOVE_EXTRA_TURN, MOVE_CAPTURE


class Rules:
    """Handles Kalah game rules and move execution."""
    
    @staticmethod
    def get_legal_moves(board: Board, player: int) -> List[int]:
        legal_moves = []
        if player == PLAYER_SOUTH:
            for i in range(board.pits_per_row):
                if board.pits[i] > 0:
                    legal_moves.append(i)
        else:  # PLAYER_NORTH
            for i in range(board.pits_per_row):
                pit_index = board.pits_per_row + i
                if board.pits[pit_index] > 0:
                    legal_moves.append(i)
        return legal_moves

    @staticmethod
    def apply_move(board: Board, player: int, pit_index: int) -> Tuple[Board, int, int]:
        """
        Robust sowing using a linear CCW position list:
        positions: [S0, S1, ..., S(p-1), SOUTH_KALAH, N0, N1, ..., N(p-1), NORTH_KALAH]
        Note: the mapping of N0..N(p-1) here corresponds to the internal pit indices
              which are stored in board.pits as [S0..S(p-1), N0..N(p-1)].
        We start from the position corresponding to the chosen pit, and advance one step
        per stone, skipping the opponent's kalah when encountered.
        """
        new_board = board.copy()
        ppr = new_board.pits_per_row

        # translate player and actual pit index in board.pits
        if player == PLAYER_SOUTH:
            actual_pit = pit_index
            opponent = PLAYER_NORTH
        else:
            actual_pit = ppr + pit_index
            opponent = PLAYER_SOUTH

        # pick up
        counters = new_board.pits[actual_pit]
        if counters == 0:
            raise ValueError("Cannot move from empty pit")
        new_board.pits[actual_pit] = 0

        # positions length = 2*ppr + 2 (two Kalahs)
        # index mapping for positions:
        # pos 0..ppr-1 -> pit indices 0..ppr-1 (south pits)
        # pos ppr     -> south_kalah
        # pos ppr+1..ppr+ppr -> pit indices ppr..2*ppr-1 (north pits)
        # pos 2*ppr+1 -> north_kalah
        len_positions = 2 * ppr + 2
        south_kalah_pos = ppr
        north_kalah_pos = 2 * ppr + 1

        # map actual_pit (0..2*ppr-1) -> position index in this sequence
        if actual_pit < ppr:
            pos_index = actual_pit
        else:
            # north pits are shifted by one position because of south_kalah in the positions list
            pos_index = actual_pit + 1

        last_was_kalah = False
        last_pit_index = None

        for _ in range(counters):
            # advance to next position (one step CCW)
            pos_index = (pos_index + 1) % len_positions

            # skip opponent's kalah
            if (pos_index == south_kalah_pos and opponent == PLAYER_SOUTH) or \
               (pos_index == north_kalah_pos and opponent == PLAYER_NORTH):
                pos_index = (pos_index + 1) % len_positions

            # place stone according to pos_index
            if pos_index == south_kalah_pos:
                new_board.south_kalah += 1
                last_was_kalah = (player == PLAYER_SOUTH)
                last_pit_index = None
            elif pos_index == north_kalah_pos:
                new_board.north_kalah += 1
                last_was_kalah = (player == PLAYER_NORTH)
                last_pit_index = None
            else:
                # map back to board.pits index
                if pos_index < ppr:
                    pit_idx = pos_index
                else:
                    # north pits area (shifted by one)
                    pit_idx = pos_index - 1
                new_board.pits[pit_idx] += 1
                last_was_kalah = False
                last_pit_index = pit_idx

        # determine result
        move_type = MOVE_NORMAL

        if last_was_kalah:
            move_type = MOVE_EXTRA_TURN
            next_player = player
        else:
            # capture: last stone landed in an own empty pit (now has 1) and opposite has >0
            if (last_pit_index is not None and
                Rules._is_own_pit(last_pit_index, player, ppr) and
                new_board.pits[last_pit_index] == 1):
                opposite = Rules._get_opposite_pit(last_pit_index, ppr)
                if new_board.pits[opposite] > 0:
                    captured = new_board.pits[opposite] + 1
                    new_board.pits[opposite] = 0
                    new_board.pits[last_pit_index] = 0
                    if player == PLAYER_SOUTH:
                        new_board.south_kalah += captured
                    else:
                        new_board.north_kalah += captured
                    move_type = MOVE_CAPTURE
                    next_player = 1 - player
                else:
                    next_player = 1 - player
            else:
                next_player = 1 - player

        return new_board, move_type, next_player

    @staticmethod
    def _is_own_pit(pit_index: int, player: int, pits_per_row: int) -> bool:
        if player == PLAYER_SOUTH:
            return 0 <= pit_index < pits_per_row
        else:
            return pits_per_row <= pit_index < 2 * pits_per_row

    @staticmethod
    def _get_opposite_pit(pit_index: int, pits_per_row: int) -> int:
        if pit_index < pits_per_row:
            return 2 * pits_per_row - 1 - pit_index
        else:
            return pits_per_row - 1 - (pit_index - pits_per_row)

    @staticmethod
    def is_game_over(board: Board) -> bool:
        return board.is_empty_row(PLAYER_SOUTH) or board.is_empty_row(PLAYER_NORTH)

    @staticmethod
    def finalize_game(board: Board) -> Board:
        final_board = board.copy()
        if final_board.is_empty_row(PLAYER_SOUTH):
            for i in range(final_board.pits_per_row):
                final_board.north_kalah += final_board.pits[final_board.pits_per_row + i]
                final_board.pits[final_board.pits_per_row + i] = 0
        elif final_board.is_empty_row(PLAYER_NORTH):
            for i in range(final_board.pits_per_row):
                final_board.south_kalah += final_board.pits[i]
                final_board.pits[i] = 0
        return final_board

    @staticmethod
    def get_winner(board: Board) -> Optional[int]:
        if not Rules.is_game_over(board):
            return None
        final_board = Rules.finalize_game(board)
        south_score = final_board.south_kalah
        north_score = final_board.north_kalah
        if south_score > north_score:
            return PLAYER_SOUTH
        elif north_score > south_score:
            return PLAYER_NORTH
        else:
            return None
