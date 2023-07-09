from .player import Player
from .piece import Piece, INITIAL_BOARD, MOVEMENT
from .position import Position
from .validator import Validator
from .threaten import Threaten
from copy import copy


class Game:

    def __init__(self):
        #self.board = []
        self.players = [Player(i) for i in range(4)]
        self.current_player = self.players[0]
        self.init_board()
        self.checkmated_player = 0

    def init_board(self) -> None:
        self.board = [[Piece.empty_piece() for __ in range(9)]
                      for _ in range(9)]  #left-top corner (0,0)
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
            self.create_threaten(self.piece_at(kings[i]), kings[i], i)
        for i in range(4):
            for c in INITIAL_BOARD:
                pos = Position(c[1], c[2])
                pos.rotate((i + 3) % 4)
                pos += kings[i]
                ch = self.piece_at(pos)
                ch.id = c[0]
                ch.belongto = i
                self.create_threaten(ch, pos, i)

    def piece_at(self, pos):
        if not pos.is_vaild_pos():
            return Piece.empty_piece()
        return self.board[pos.x][pos.y]

    def threaten_piece_at(self, pos):
        if isinstance(pos, Position) or not pos.is_vaild_pos():
            return set()
        return self.threaten_piece[pos.x][pos.y]

    #放子->合法性檢驗->王手檢驗->PASS
    def on_place(self, piece, from_pos, new_pos) -> bool:
        piece.belongto = self.current_player.id

        #vaildate
        if not Validator.is_vaild_place(piece, from_pos, new_pos):
            return False

        eaten_piece = copy(self.piece_at(new_pos))
        from_piece = Piece.empty_piece() if from_pos.is_empty_pos() else copy(self.piece_at(from_pos))

        #threaten
        Threaten.remove_threaten(self, eaten_piece, new_pos)
        self.board[new_pos.x][new_pos.y] = piece.empty_piece()
        Threaten.remove_threaten(self, from_piece, from_pos)

        #if move from exist piece, update old pos piece
        if not from_pos.is_empty_pos():
            self.board[from_pos.x][from_pos.y] = Piece.empty_piece()
        else:
            self.current_player.holding_piece[piece.id] -= 1
        #get the piece on moving into
        if not eaten_piece.is_empty_piece():
            self.current_player.holding_piece[eaten_piece.id] += 1
        self.board[new_pos.x][new_pos.y] = piece

        #threaten2
        Threaten.create_threaten(self, piece, new_pos)

        #update king pos
        if piece.id == 'k':
            self.current_player.king_pos = new_pos

        #king must be safe after move
        kp = self.current_player.king_pos
        threatened = False
        for ch in self.threaten_piece_at(kp):
            if ch.belongto != self.current_player.id:
                if True:
                    print('kkk')
                    print(ch)
                threatened = True
        
        if threatened:  #undo
            if piece.id == 'k':
                self.current_player.king_pos = from_pos
            Threaten.remove_threaten(self, piece, new_pos)
            if not from_piece.is_empty_piece():
                self.board[from_pos.x][from_pos.y] = from_piece
                Threaten.create_threaten(self, from_piece, from_pos)
            else:
                self.current_player.holding_piece[piece.id] += 1
            if not eaten_piece.is_empty_piece():
                self.board[new_pos.x][new_pos.y] = eaten_piece
                Threaten.create_threaten(self, eaten_piece, new_pos)
                self.current_player.holding_piece[eaten_piece.id] -= 1
            else:
                self.board[new_pos.x][new_pos.y] = Piece.empty_piece()
            return False

        self.next_turn()
        return True

    def is_checkmate(game, piece, new_pos, king_pos):
        can_eliminate_piece = False
        can_escape_piece = False
        king_piece = game.piece_at(king_pos)
        for eat_piece in game.threaten_piece_at(new_pos):
            if eat_piece.id == king_piece.belongto:
                can_eliminate_piece = True
                break
        for reachable in MOVEMENT['k']:
            king_can_go = king_pos + reachable
            cant_go = False
            for threating_piece in game.threaten_piece_at(king_can_go):
                if threating_piece.id != king_piece.belongto:
                    cant_go = True
                    break
            if not cant_go:
                can_escape_piece = True
                break
        return can_eliminate_piece or can_escape_piece

    def next_turn(self) -> bool:
        if self.checkmated_player >= 3:
            return
        #處理下一位輪到誰
        checked_player = self.get_checked_player()
        if checked_player != -1:
            self.current_player = self.players[checked_player]
        else:
            self.current_player = self.players[(self.current_player.id + 1) % 4]
        if self.current_player.checkmated:
            self.next_turn()

    def get_checked_player(self):
        now_id = self.current_player.id
        ret = 10
        for player in self.players:
            kp = player.king_pos
            for ch in self.threaten_piece_at(kp):
                if ch.belongto != player.id:
                    id = player.id
                    if id < now_id:
                        id += 4
                    ret = min(ret, id)
                    break
        if ret == 10:
            return -1
        else:
            return ret % 4
