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
            Threaten.create_threaten(self, self.piece_at(kings[i]), kings[i])
        for i in range(4):
            for c in INITIAL_BOARD:
                pos = Position(c[1], c[2])
                pos.rotate((i + 3) % 4)
                pos += kings[i]
                ch = self.piece_at(pos)
                ch.id = c[0]
                ch.belongto = i
                Threaten.create_threaten(self, ch, pos)

    def piece_at(self, pos):
        if not pos.is_vaild_pos():
            return Piece.empty_piece()
        return self.board[pos.x][pos.y]

    def threaten_piece_at(self, pos):
        if not (isinstance(pos, Position) and pos.is_vaild_pos()):
            return set()
        return self.threaten_piece[pos.x][pos.y]

    #放子->合法性檢驗->王手檢驗->PASS
    def on_place(self, piece, from_pos, new_pos) -> bool:
        debug = False

        piece.belongto = self.current_player.id
        
        #vaildate
        if not Validator.is_vaild_place(self, piece, from_pos, new_pos):
            return False

        eaten_piece = copy(self.piece_at(new_pos))
        from_piece = Piece.empty_piece() if from_pos.is_empty_pos() else copy(self.piece_at(from_pos))

        #if move from exist piece, update old pos piece
        if not from_pos.is_empty_pos():
            self.board[from_pos.x][from_pos.y] = Piece.empty_piece()
        else:
            self.current_player.holding_piece[piece.id] -= 1

        #threaten
        self.board[new_pos.x][new_pos.y] = piece.empty_piece()
        Threaten.remove_threaten(self, eaten_piece, new_pos)
        Threaten.remove_threaten(self, from_piece, from_pos)
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
                    print(kp)
                threatened = True
                if not debug:
                    break
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
            
        #debug
        if False:
            for i in range(9):
                print('d' + str(i) + 's')
                for de in self.threaten_piece_at(Position(i, 4)):
                    print(de)
                print('d' + str(i) + 'e')
                
        self.handle_checkmate(piece, new_pos)
        
        self.next_turn()
        return True

    def checkmate_normal(self, new_pos, player):
        can_eliminate_piece = False
        can_escape_piece = False
        king_pos = player.king_pos
        king_piece = self.piece_at(king_pos)
        for eat_piece in self.threaten_piece_at(new_pos):
            if eat_piece.id == 'k':
                continue
            if eat_piece.belongto == king_piece.belongto:
                can_eliminate_piece = True
                break
        for reachable in MOVEMENT['k']:
            king_can_go = king_pos + reachable
            if not king_can_go.is_vaild_pos():
                continue
            if self.piece_at(king_can_go).belongto == king_piece.belongto:
                continue
            cant_go = False
            for threating_piece in self.threaten_piece_at(king_can_go):
                if threating_piece.belongto != king_piece.belongto:
                    cant_go = True
            if not cant_go:
                can_escape_piece = True
                break
        return not (can_eliminate_piece or can_escape_piece)

    def checkmate_rock(self, new_pos, player):
        can_eliminate_piece = False
        can_escape_piece = False
        can_block_piece = False
        king_pos = player.king_pos
        king_piece = self.piece_at(king_pos)
        for eat_piece in self.threaten_piece_at(new_pos):
            if eat_piece.id == 'k':
                continue
            if eat_piece.belongto == king_piece.belongto:
                can_eliminate_piece = True
                break
        for reachable in MOVEMENT['k']:
            king_can_go = king_pos + reachable
            if not king_can_go.is_vaild_pos():
                continue
            if ((king_can_go.x == new_pos.x or king_can_go.y == new_pos.y) and
                king_can_go != new_pos):
                continue
            if self.piece_at(king_can_go).belongto == king_piece.belongto:
                continue
            cant_go = False
            for threating_piece in self.threaten_piece_at(king_can_go):
                if threating_piece.belongto != king_piece.belongto:
                    cant_go = True
            if not cant_go:
                can_escape_piece = True
                break
        delta_pos = Position.get_unit_way(king_pos, new_pos)
        tmp_pos = copy(king_pos) + delta_pos
        while tmp_pos != new_pos:
            if (player.holding_piece['p'] > 0 and 
                Validator.is_vaild_drop_pawn(self, tmp_pos, player.id)):
                can_block_piece = True
                break
            for id, sz in player.holding_piece.items():
                if sz > 0 and id != 'p':
                    can_block_piece = True
                    break
            tmp_pos += delta_pos
        return not (can_eliminate_piece or can_escape_piece or can_block_piece)
    
    def is_checkmated(self, piece, new_pos, player):
        king_pos = player.king_pos
        if piece.id == 'r':
            if new_pos.x != king_pos.x and new_pos.y != king_pos.y:
                return False
            return self.checkmate_rock(new_pos, player)
        else:
            return self.checkmate_normal(new_pos, player)

    def handle_checkmate(self, piece, new_pos):
        for player in self.players:
            if player.checkmated or player.id == piece.belongto:
                continue
            king_pos = player.king_pos
            threatened = False
            for ch in self.threaten_piece_at(king_pos):
                if ch.belongto != player.id:
                    threatened = True
                    break
            if threatened and self.is_checkmated(piece, new_pos, player):
                player.checkmated = True
                self.current_player = player
                print('Player ' + str(player.id) + ' dead')
                for i, row in enumerate(self.board):
                    for j, col in enumerate(row):
                        if col.belongto == player.id:
                            Threaten.remove_threaten(self, col, Position(i, j))
    
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
            if player.checkmated:
                continue
            kp = player.king_pos
            for ch in self.threaten_piece_at(kp):
                if ch.belongto != player.id:
                    id = player.id if player.id >= now_id else player.id + 4
                    ret = min(ret, id)
                    break
        if ret == 10:
            return -1
        else:
            return ret % 4
