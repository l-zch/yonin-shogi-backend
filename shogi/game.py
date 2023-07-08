from .player import Player
from .piece import Piece, INITIAL_BOARD, MOVEMENT
from .utils import Position
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

    def create_threaten(self, piece, pos, only=False):
        threaten_piece = copy(piece)
        threaten_piece.init_threaten_piece(pos)
        way = threaten_piece.belongto

        #handle blocking rock range line
        if not only:
            for piece_r in self.threaten_piece_at(pos):
                if piece_r.id == 'r':
                    unit_way = Position.get_unit_way(piece_r.pos, pos)
                    new_pos = pos + unit_way
                    while new_pos.is_vaild_pos():
                        self.threaten_piece_at(new_pos).discard(piece_r)
                        if not self.piece_at(new_pos).is_empty_piece():
                            break
                        new_pos += unit_way

        now_id = threaten_piece.id
        if threaten_piece.id == 'r':
            if threaten_piece.promoted:
                for reachable in MOVEMENT['R']:
                    new_pos = pos + reachable
                    self.threaten_piece_at(new_pos).add(threaten_piece)
            ways = MOVEMENT['r']
            for w in ways:
                new_pos = pos + w
                while new_pos.is_vaild_pos():
                    self.threaten_piece_at(new_pos).add(threaten_piece)
                    if not self.piece_at(new_pos).is_empty_piece():
                        break
                    new_pos += w
            if only:
                return
            #if a king in a row or a col
            for player in self.players:
                if player.id == self.current_player.id:
                    continue
                kp = player.king_pos
                if kp.x == pos.x:
                    unit_way = Position.get_unit_way(kp, pos)
                    blockers = []
                    new_pos = kp + unit_way
                    while new_pos != pos:
                        if not self.piece_at(new_pos).is_empty_piece():
                            _ch = copy(self.piece_at(new_pos))
                            _ch.init_threaten_piece(new_pos)
                            blockers.append(_ch)
                        new_pos += unit_way
                    if len(blockers) != 1:
                        continue
                    if blockers[0].belongto == player.id:
                        self.remove_threaten(blockers[0], blockers[0].pos,
                                             True)

            return

        if threaten_piece.promoted:
            now_id = 'g'
        for reachable in MOVEMENT[now_id]:
            _reachable = copy(reachable)
            _reachable.rotate(way)
            new_pos = pos + _reachable
            self.threaten_piece_at(new_pos).add(threaten_piece)

        if threaten_piece.id == 'k':
            for unit_way in MOVEMENT['r']:
                new_pos = pos + unit_way
                blockers = []
                while new_pos.is_vaild_pos():
                    ch = self.piece_at(new_pos)
                    if ch.id == 'r' and ch.belongto != piece.belongto:
                        if len(blockers) != 1:
                            break
                        if blockers[0].belongto == piece.belongto:
                            self.remove_threaten(blockers[0], blockers[0].pos,
                                                 True)
                            two_way = [unit_way, unit_way * -1]
                            for w in two_way:
                                if w in MOVEMENT[blockers[0].id]:
                                    self.threaten_piece_at(blockers[0].pos +
                                                           w).add(blockers[0])
                        break
                    elif not ch.is_empty_piece():
                        _ch = copy(ch)
                        _ch.init_threaten_piece(new_pos)
                        blockers.append(_ch)
                    new_pos += unit_way

    def remove_threaten(self, piece, pos, only=False):
        threaten_piece = copy(piece)
        threaten_piece.init_threaten_piece(pos)
        way = threaten_piece.belongto

        #handle blocking rock range line
        if not only:
            for piece_r in self.threaten_piece_at(pos):
                if piece_r.id == 'r':
                    unit_way = Position.get_unit_way(piece_r.pos, pos)
                    new_pos = pos + unit_way
                    while new_pos.is_vaild_pos():
                        self.threaten_piece_at(new_pos).add(piece_r)
                        if not self.piece_at(new_pos).is_empty_piece():
                            break
                        new_pos += unit_way

        now_id = threaten_piece.id
        if threaten_piece.id == 'r':
            if threaten_piece.promoted:
                for reachable in MOVEMENT['R']:
                    new_pos = pos + reachable
                    self.threaten_piece_at(new_pos).discard(threaten_piece)
            ways = MOVEMENT['r']
            for w in ways:
                new_pos = pos + w
                while new_pos.is_vaild_pos():
                    self.threaten_piece_at(new_pos).discard(threaten_piece)
                    if not self.piece_at(new_pos).is_empty_piece():
                        break
                    new_pos = new_pos + w
            if only:
                return
            #if a king in a row or a col
            for player in self.players:
                if player.id == self.current_player.id:
                    continue
                kp = player.king_pos
                if kp.x == pos.x:
                    unit_way = Position.get_unit_way(kp, pos)
                    blockers = []
                    new_pos = kp + unit_way
                    while new_pos != pos:
                        if not self.piece_at(new_pos).is_empty_piece():
                            _ch = copy(self.piece_at(new_pos))
                            _ch.init_threaten_piece(new_pos)
                            blockers.append(_ch)
                        new_pos += unit_way
                    sz = len(blockers)
                    if sz != 1:
                        continue
                    if blockers[0].belongto == player.id:
                        self.create_threaten(blockers[0], blockers[0].pos,
                                             True)
            return
        if threaten_piece.promoted:
            now_id = 'g'
        for reachable in MOVEMENT[now_id]:
            _reachable = copy(reachable)
            _reachable.rotate(way)
            new_pos = pos + _reachable
            self.threaten_piece_at(new_pos).discard(threaten_piece)

        if threaten_piece.id == 'k':
            for unit_way in MOVEMENT['r']:
                new_pos = pos + unit_way
                blockers = []
                while new_pos.is_vaild_pos():
                    ch = self.piece_at(new_pos)
                    if ch.id == 'r' and ch.belongto != piece.belongto:
                        if len(blockers) != 1:
                            break
                        if blockers[0].belongto == piece.belongto:
                            self.create_threaten(blockers[0], blockers[0].pos,
                                                 True)
                        break
                    elif not ch.is_empty_piece():
                        _ch = copy(ch)
                        _ch.init_threaten_piece(new_pos)
                        blockers.append(_ch)
                    new_pos += unit_way

    def piece_at(self, pos):
        if not pos.is_vaild_pos():
            return Piece.empty_piece()
        return self.board[pos.x][pos.y]

    def threaten_piece_at(self, pos):
        if not pos or not pos.is_vaild_pos():
            return set()
        return self.threaten_piece[pos.x][pos.y]

    #放子->合法性檢驗->王手檢驗->PASS
    def on_place(self, piece, from_pos, new_pos) -> bool:
        debug = True
        #vaildate pos
        if not from_pos.is_vaild_pos() and not from_pos.is_empty_pos():
            return False
        if not new_pos.is_vaild_pos():
            return False

        piece.belongto = self.current_player.id

        #vaildate move
        if not self.is_vaild_place(piece, from_pos, new_pos):
            return False

        _old = None
        if not self.piece_at(new_pos).is_empty_piece():
            _old = copy(self.piece_at(new_pos))

        #threaten
        if _old is not None:
            self.remove_threaten(_old, new_pos)
        self.board[new_pos.x][new_pos.y] = piece.empty_piece()
        if not from_pos.is_empty_pos():
            self.remove_threaten(piece, from_pos)

        #debug
        if debug:
            for i in range(9):
                print('e' + str(i) + 's')
                for de in self.threaten_piece_at(Position(4, i)):
                    print(de)
                print('e' + str(i) + 'e')

        #if move from exist piece, update old pos piece
        if not from_pos.is_empty_pos():
            self.board[from_pos.x][from_pos.y] = Piece.empty_piece()
        else:
            self.current_player.holding_piece[piece.id] -= 1
        #get the piece on moving into
        if _old is not None:
            self.current_player.holding_piece[_old.id] += 1
        self.board[new_pos.x][new_pos.y] = piece

        #threaten2
        self.create_threaten(piece, new_pos)

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
                if not debug:
                    break
        if threatened:  #undo
            if piece.id == 'k':
                self.current_player.king_pos = from_pos
            self.remove_threaten(piece, new_pos)
            if not from_pos.is_empty_pos():
                self.board[from_pos.x][from_pos.y] = piece
                self.create_threaten(piece, from_pos)
            else:
                self.current_player.holding_piece[piece.id] += 1
            if _old is not None:
                self.board[new_pos.x][new_pos.y] = _old
                self.create_threaten(_old, new_pos)
                self.current_player.holding_piece[_old.id] -= 1
            else:
                self.board[new_pos.x][new_pos.y] = Piece.empty_piece()
            return False

        self.next_turn()

        #debug
        if debug:
            for i in range(9):
                print('d' + str(i) + 's')
                for de in self.threaten_piece_at(Position(4, i)):
                    print(de)
                print('d' + str(i) + 'e')
        return True

    def is_vaild_movement(self, piece, from_pos, new_pos):
        if self.piece_at(from_pos).is_empty_piece():
                return False
        from_piece = self.piece_at(from_pos)
        if (from_piece.belongto != piece.belongto or
                #from_piece.promoted != piece.promoted or
                from_piece.id != piece.id):
            return False
        if from_piece.promoted != piece.promoted:
            if from_piece.promoted:
                return False

        facing = self.current_player.id
        delta_pos = new_pos - from_pos
        find = False
        now_id = 'g' if from_piece.promoted else from_piece.id
        if from_piece.id == 'r':
            delta_pos = Position.get_unit_way(from_pos, new_pos)
            now_id = 'R' if from_piece.promoted else now_id
        for vaild_pos in MOVEMENT[now_id]:
            _vaild_pos = copy(vaild_pos)
            _vaild_pos.rotate(facing)
            if delta_pos == _vaild_pos:
                find = True
        return find

    def is_checkmate(self, piece, new_pos, king_pos):
        can_eliminate_piece = False
        can_escape_piece = False
        king_piece = self.piece_at(king_pos)
        for eat_piece in self.threaten_piece_at(new_pos):
            if eat_piece.id == king_piece.belongto:
                can_eliminate_piece = True
                break
        for reachable in MOVEMENT['k']:
            king_can_go = king_pos + reachable
            cant_go = False
            for threating_piece in self.threaten_piece_at(king_can_go):
                if threating_piece.id != king_piece.belongto:
                    cant_go = True
                    break
            if not cant_go:
                can_escape_piece = True
                break
        return can_eliminate_piece or can_escape_piece

    def is_vaild_drop(self, piece, new_pos):
        if not self.piece_at(new_pos).is_empty_piece():
            return False
        left_in_hand = self.current_player.holding_piece[piece.id]
        if not left_in_hand or left_in_hand <= 0:
            return False
        if piece.promoted:
            return False
        if piece.id != 'p':
            return True
        facing = self.current_player.id
        if facing % 2 == 0:
            if ((new_pos.x == 0 and facing == 0)
            or (new_pos.x == 8 and facing == 2)):
                return False
            for row in range(9):
                ch = self.board[row][new_pos.y]
                if ch.belongto == facing and ch.id == 'p':
                    return False
        else:
            if ((new_pos.y == 8 and facing == 1)
            or (new_pos.y == 0 and facing == 3)):
                return False
            for col in range(9):
                ch = self.board[new_pos.x][col]
                if ch.belongto == facing and ch.id == 'p':
                    return False
        unit_forward = Position(0, 1)
        unit_forward.rotate(facing)
        forward_pos = new_pos + unit_forward
        forward_ch = self.piece_at(forward_pos)
        if forward_ch.id == 'k' and forward_ch.belongto != facing:  #打步詰
            return self.is_checkmate(piece, new_pos, forward_pos)
        else:
            return True
    
    
    def is_vaild_place(self, piece, from_pos, new_pos) -> bool:
        # 檢查持駒or移動合法 f
        # 打步詰 f
        # 二步 f
        # 打入位置合法 f
        # 新位置若有棋非己方棋才可移動過去 f
        # 若升變，升變是否合法
        if self.piece_at(new_pos).belongto == self.current_player.id:
            return False
        if from_pos.is_empty_pos():
            return self.is_vaild_drop(piece, new_pos)
        else:
            return self.is_vaild_movement(piece, from_pos, new_pos)

    def next_turn(self) -> bool:
        if self.checkmated_player >= 3:
            return
        #處理下一位輪到誰
        checked_player = self.get_checked_player()
        if checked_player != -1:
            self.current_player = self.players[checked_player]
        else:
            self.current_player = self.players[(self.current_player.id + 1) %
                                               4]
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
