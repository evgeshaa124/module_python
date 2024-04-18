from abc import ABC, abstractmethod
from enum import Enum
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

class Color(Enum):
    WHITE = 'white'
    BLACK = 'black'

class Move(BaseModel):
    start_pos: tuple
    end_pos: tuple
class Piece(ABC):
    def __init__(self, color: Color):
        self.color = color

    @abstractmethod
    def can_move(self, board, start_pos, end_pos):
        pass

class King(Piece):
    def can_move(self, board, start_pos, end_pos):
        start_row, start_col = start_pos
        end_row, end_col = end_pos

        if abs(end_row - start_row) <= 1 and abs(end_col - start_col) <= 1:
            if not board.is_occupied(end_pos) or board.get_piece(end_pos).color != self.color:
                return True
        return False

class Queen(Piece):
    def can_move(self, board, start_pos, end_pos):
        start_row, start_col = start_pos
        end_row, end_col = end_pos

        if start_row == end_row or start_col == end_col or abs(end_row - start_row) == abs(end_col - start_col):
            row_step = 0 if start_row == end_row else (1 if end_row > start_row else -1)
            col_step = 0 if start_col == end_col else (1 if end_col > start_col else -1)
            current_row, current_col = start_row + row_step, start_col + col_step

            while (current_row, current_col) != (end_row, end_col):
                if board.is_occupied((current_row, current_col)):
                    return False
                current_row += row_step
                current_col += col_step

            if not board.is_occupied(end_pos) or board.get_piece(end_pos).color != self.color:
                return True

        return False

class Rook(Piece):
    def can_move(self, board, start_pos, end_pos):
        start_row, start_col = start_pos
        end_row, end_col = end_pos

        if start_row == end_row or start_col == end_col:
            row_step = 0 if start_row == end_row else (1 if end_row > start_row else -1)
            col_step = 0 if start_col == end_col else (1 if end_col > start_col else -1)
            current_row, current_col = start_row + row_step, start_col + col_step

            while (current_row, current_col) != (end_row, end_col):
                if board.is_occupied((current_row, current_col)):
                    return False
                current_row += row_step
                current_col += col_step

            if not board.is_occupied(end_pos) or board.get_piece(end_pos).color != self.color:
                return True

        return False

class Bishop(Piece):
        def can_move(self, board, start_pos, end_pos):
            start_row, start_col = start_pos
            end_row, end_col = end_pos

            if abs(end_row - start_row) == abs(end_col - start_col):
                row_step = 1 if end_row > start_row else -1
                col_step = 1 if end_col > start_col else -1
                current_row, current_col = start_row + row_step, start_col + col_step

                while (current_row, current_col) != (end_row, end_col):
                    if board.is_occupied((current_row, current_col)):
                        return False
                    current_row += row_step
                    current_col += col_step

                if not board.is_occupied(end_pos) or board.get_piece(end_pos).color != self.color:
                    return True

            return False

class Knight(Piece):
    def can_move(self, board, start_pos, end_pos):
        start_row, start_col = start_pos
        end_row, end_col = end_pos

        if (abs(end_row - start_row) == 2 and abs(end_col - start_col) == 1) or \
                (abs(end_row - start_row) == 1 and abs(end_col - start_col) == 2):
            if not board.is_occupied(end_pos) or board.get_piece(end_pos).color != self.color:
                return True

        return False

class Pawn(Piece):
    def can_move(self, board, start_pos, end_pos):
        start_row, start_col = start_pos
        end_row, end_col = end_pos

        row_step = 1 if self.color == Color.WHITE else -1

        if start_col == end_col:
            if start_row + row_step == end_row:
                if not board.is_occupied(end_pos):
                    return True
            elif start_row + 2 * row_step == end_row and \
                    ((self.color == Color.WHITE and start_row == 1) or \
                     (self.color == Color.BLACK and start_row == 6)):
                if not board.is_occupied((start_row + row_step, start_col)) and \
                        not board.is_occupied(end_pos):
                    return True
        else:
            if abs(start_col - end_col) == 1 and start_row + row_step == end_row:
                target_piece = board.get_piece(end_pos)
                if target_piece is not None and target_piece.color != self.color:
                    return True

        return False

class Board:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.setup_pieces()

    def setup_pieces(self):

        self.board[0][0] = Rook(Color.WHITE)
        self.board[0][1] = Knight(Color.WHITE)
        self.board[0][2] = Bishop(Color.WHITE)
        self.board[0][3] = Queen(Color.WHITE)
        self.board[0][4] = King(Color.WHITE)
        self.board[0][5] = Bishop(Color.WHITE)
        self.board[0][6] = Knight(Color.WHITE)
        self.board[0][7] = Rook(Color.WHITE)
        for i in range(8):
            self.board[1][i] = Pawn(Color.WHITE)

        self.board[7][0] = Rook(Color.BLACK)
        self.board[7][1] = Knight(Color.BLACK)
        self.board[7][2] = Bishop(Color.BLACK)
        self.board[7][3] = Queen(Color.BLACK)
        self.board[7][4] = King(Color.BLACK)
        self.board[7][5] = Bishop(Color.BLACK)
        self.board[7][6] = Knight(Color.BLACK)
        self.board[7][7] = Rook(Color.BLACK)
        for i in range(8):
            self.board[6][i] = Pawn(Color.BLACK)

    def is_valid_move(self, start_pos, end_pos):
        if not (0 <= start_pos[0] < 8 and 0 <= start_pos[1] < 8 and 0 <= end_pos[0] < 8 and 0 <= end_pos[1] < 8):
            return False

        piece = self.board[start_pos[0]][start_pos[1]]
        if piece is None:
            return False

        if not piece.can_move(self, start_pos, end_pos):
            return False

        target_piece = self.board[end_pos[0]][end_pos[1]]
        if target_piece is not None and target_piece.color == piece.color:
            return False

        return True

    def move_piece(self, start_pos, end_pos):
        if self.is_valid_move(start_pos, end_pos):
            self.board[end_pos[0]][end_pos[1]] = self.board[start_pos[0]][start_pos[1]]
            self.board[start_pos[0]][start_pos[1]] = None
            return True
        return False

    def to_json(self):
        return [[piece.__class__.__name__ if piece else None for piece in row] for row in self.board]

class Game:
    def __init__(self):
        self.board = Board()
        self.current_turn = Color.WHITE
        self.game_over = False

    def start_game(self):
        self.board.setup_pieces()
        self.current_turn = Color.WHITE
        self.game_over = False

    def move(self, player, start_pos, end_pos):
        # make a move
        pass

    def end_game(self):
        self.game_over = True
        return "Game over."

app = FastAPI()

@app.post("/start_game/")
def start_game():
    game.start_game()
    return {"message": "Game started."}

@app.post("/move/")
def move(move: Move):
    # make a move
    pass

@app.post("/end_game/")
def end_game():
    result = game.end_game()
    return {"message": result}

@app.get("/get_board/")
def get_board():
    return {"board": game.board.to_json()}
