from .player import Player
from .piece import Piece, INITIAL_BOARD, MOVEMENT
from .position import Position
from .validator import Validator
from copy import copy
import numpy as np


class Game:

    def __init__(self):
        self.players = [Player(i) for i in range(4)]
        self.current_player = self.players[0]
        self.init_board()
        self.checkmated_player = 0

    def init_board(self):
        self.board = [[Piece.empty_piece() for __ in range(9)] for _ in range(9)]
        self.threaten_piece = [[set() for __ in range(9)] for _ in range(9)]
        kings = [
            Position(8, 4),
            Position(4, 0),
            Position(0, 4),
            Position(4, 8)
        ]
        for i in range(4):
            self.piece_at(kings[i]).id = 'k'
            self.piece_at(kings[i]).belongto = i
            self.players[i].king_pos = kings[i]
            for c in INITIAL_BOARD:
                pos = Position(c[1], c[2])
                pos.rotate((i + 3) % 4)
                pos += kings[i]
                ch = self.piece_at(pos)
                ch.id = c[0]
                ch.belongto = i

    def piece_at(self, pos):
        if not pos.is_vaild_pos():
            return Piece.empty_piece()
        return self.board[pos.x][pos.y]

    #放子->合法性檢驗->王手檢驗->PASS
    def on_place(self, piece, from_pos, new_pos):
        piece.belongto = self.current_player.id
        
        #vaildate
        if not Validator.is_vaild_place(self, piece, from_pos, new_pos):
            return False

        eaten_piece = copy(self.piece_at(new_pos))
        from_piece = Piece.empty_piece() if from_pos.is_empty_pos() else copy(self.piece_at(from_pos))
        
        if not from_pos.is_empty_pos():
            self.board[from_pos.x][from_pos.y] = Piece.empty_piece()
        else:
            self.current_player.holding_piece[piece.id] -= 1
        
        if not eaten_piece.is_empty_piece():
            self.current_player.holding_piece[eaten_piece.id] += 1
        self.board[new_pos.x][new_pos.y] = piece

        #update king pos
        if piece.id == 'k':
            self.current_player.king_pos = new_pos

        if self.is_threatened(self.current_player):
            if piece.id == 'k':
                self.current_player.king_pos = from_pos
            self.board[new_pos.x][new_pos.y] = eaten_piece
            if not eaten_piece.is_empty_piece():
                self.current_player.holding_piece[eaten_piece.id] -= 1
            
            if not from_pos.is_empty_pos():
                self.board[from_pos.x][from_pos.y] = from_piece
            else:
                self.current_player.holding_piece[piece.id] += 1
            return False
                
        self.handle_checkmate(piece, new_pos)
        
        self.next_turn()
        return True

    def if_move(self, piece, from_pos, new_pos):
        eaten_piece = copy(self.piece_at(new_pos))
        from_piece = self.piece_at(from_pos)
        from_piece = Piece.empty_piece()
        self.board[new_pos.x][new_pos.y] = piece
        return eaten_piece, from_piece

    def undo_move(self, piece, eaten_piece, from_piece, new_pos):
        self.board[new_pos.x][new_pos.y] = eaten_piece
        from_piece = piece

    def try_place(self, pos, player):
        for kv in filter(lambda kv: kv[1] > 0, player.holding_piece.items()):
            ch = Piece(kv[0])
            ch.belongto = player.id
            if Validator.is_vaild_place(self, ch, Position.empty_pos(), pos):
                eaten_piece, from_piece = self.if_move(ch, Position.empty_pos(), pos)
                if not self.is_threatened(player):
                    self.undo_move(ch, eaten_piece, from_piece, pos)
                    return True
                self.undo_move(ch, eaten_piece, from_piece, pos)
        return False
    
    def is_checkmated(self, new_pos, player):
        king_pos = player.king_pos
        king_piece = self.piece_at(king_pos)
        for idx, val in np.ndenumerate(self.board):
            if val.belongto == player.id and Validator.is_vaild_place(self, val, Position(idx[0], idx[1]), new_pos):
                return False
            if val.is_empty_piece() and self.try_place(Position(idx[0], idx[1]), player):
                return False
        for reachable in MOVEMENT['k']:
            king_can_go = king_pos + reachable
            if not king_can_go.is_vaild_pos():
                continue
            if self.piece_at(king_can_go).belongto == king_piece.belongto:
                continue
            eaten_piece, from_piece = self.if_move(king_piece, king_pos, king_can_go)
            if not self.is_threatened(player):
                self.undo_move(king_piece, eaten_piece, from_piece, king_can_go)
                return False
            self.undo_move(king_piece, eaten_piece, from_piece, king_can_go)
        return True

    def is_threatened(self, player):
        king_pos = player.king_pos
        for reachable in MOVEMENT['k']:
            pos = copy(king_pos) + reachable
            ch = self.piece_at(pos)
            if ch.is_empty_piece() or ch.belongto == player.id:
                continue
            _reachable = copy(reachable) * -1
            if _reachable in MOVEMENT[ch.id]:
                return True
        for ranged in MOVEMENT['r']:
            pos = copy(king_pos) + ranged
            while pos.is_vaild_pos() and self.piece_at(pos).is_empty_piece():
                pos += ranged
            ch = self.piece_at(pos)
            if pos.is_vaild_pos() and ch.belongto != player.id and ch.id == 'r':
                return True
        return False

    def handle_checkmate(self, piece, new_pos):
        for player in filter(lambda player: not player.checkmated and player.id != piece.belongto, self.players):
            if self.is_threatened(player) and self.is_checkmated(new_pos, player):
                player.checkmated = True
                self.current_player = player
                self.checkmated_player += 1
                print('Player ' + str(player.id) + ' dead')
    
    def next_turn(self):
        if self.checkmated_player >= 3:
            return
        #處理下一位輪到誰
        checked_player = self.get_checked_player()
        self.current_player = self.players[checked_player] if checked_player != -1 \
                                                            else self.players[(self.current_player.id + 1) % 4]
        if self.current_player.checkmated:
            self.next_turn()

    def get_checked_player(self):
        now_id = self.current_player.id
        ret = 10
        for player in filter(lambda player: not player.checkmated and self.is_threatened(player), self.players):
            id = player.id if player.id >= now_id else player.id + 4
            ret = min(ret, id)
            break
        return -1 if ret == 10 else ret % 4
