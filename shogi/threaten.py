from .position import Position
from .piece import MOVEMENT
from copy import copy

class Threaten:

    @staticmethod
    def add_piece_to_set(game, pos, piece):
        game.threaten_piece_at(pos).add(piece)
        
    @staticmethod
    def discard_piece_to_set(game, pos, piece):
        game.threaten_piece_at(pos).discard(piece)

    @staticmethod
    def handle_rock_line(game, pos, func2):
        #handle blocking or unblocking rock range line
        for piece_r in game.threaten_piece_at(pos):
            if piece_r.id == 'r':
                unit_way = Position.get_unit_way(piece_r.pos, pos)
                new_pos = pos + unit_way
                while new_pos.is_vaild_pos():
                    func2(game, new_pos, piece_r)
                    if not game.piece_at(new_pos).is_empty_piece():
                        break
                    new_pos += unit_way

    @staticmethod
    def handle_rock_threaten(game, threaten_piece, pos, func1):
        if threaten_piece.promoted:
            for reachable in MOVEMENT['R']:
                new_pos = pos + reachable
                func1(game, new_pos, threaten_piece)
        for w in MOVEMENT['r']:
            new_pos = pos + w
            while new_pos.is_vaild_pos():
                func1(game, new_pos, threaten_piece)
                if not game.piece_at(new_pos).is_empty_piece():
                    break
                new_pos += w

    @staticmethod
    def handle_rock_king(game, pos, func3):
        #if a king in a row or a col
        for player in game.players:
            if player.id == game.current_player.id:
                continue
            kp = copy(player.king_pos)
            if kp.x == pos.x or kp.y == pos.y:
                unit_way = Position.get_unit_way(kp, pos)
                blockers = []
                new_pos = kp + unit_way
                while new_pos != pos:
                    if not game.piece_at(new_pos).is_empty_piece():
                        _ch = copy(game.piece_at(new_pos))
                        _ch.init_threaten_piece(new_pos)
                        blockers.append(_ch)
                    new_pos += unit_way
                if len(blockers) != 1:
                    continue
                if blockers[0].belongto == player.id:
                    func3(game, blockers[0], blockers[0].pos, True)
                    if func3 == Threaten.remove_threaten:
                        Threaten.create_blocker(game, blockers[0], unit_way, kp, pos)

    @staticmethod
    def create_blocker(game, piece, unit_way, pos, new_pos):
        if piece.id == 'r':
            tmp_pos = copy(pos)
            while True:
                if tmp_pos == piece.pos:
                    tmp_pos += unit_way
                Threaten.add_piece_to_set(game, tmp_pos, piece)
                if tmp_pos == new_pos:
                    break
                tmp_pos += unit_way
        else:
            two_way = [unit_way, unit_way * -1]
            blocker_id = 'g' if piece.promoted else piece.id
            if two_way[0] in MOVEMENT[blocker_id]:
                Threaten.add_piece_to_set(game, piece.pos + two_way[0], piece)
            if two_way[1] in MOVEMENT[blocker_id]:
                Threaten.add_piece_to_set(game, piece.pos + two_way[1], piece)

    @classmethod
    def handle_blocker_king(cls, game, id, pos, func1, func3):
        for unit_way in MOVEMENT['r']:
            new_pos = pos + unit_way
            blockers = []
            while new_pos.is_vaild_pos():
                ch = game.piece_at(new_pos)
                if ch.id == 'r' and ch.belongto != id:
                    if len(blockers) != 1:
                        break
                    if blockers[0].belongto == id:
                        func3(game, blockers[0], blockers[0].pos, True)
                        if func3 == Threaten.remove_threaten:
                            cls.create_blocker(game, blockers[0], unit_way, pos, new_pos)
                    break
                elif not ch.is_empty_piece():
                    _ch = copy(ch)
                    _ch.init_threaten_piece(new_pos)
                    blockers.append(_ch)
                new_pos += unit_way

    @classmethod
    def handle_middle(cls, game, id, pos, func1, func3):
        king_pos = copy(game.players[id].king_pos)
        if king_pos.x == pos.x or king_pos.y == pos.y:
            cls.handle_blocker_king(game, id, king_pos, func1, func3)

    @classmethod
    def handle_threaten(cls, game, piece, pos, only, func1, func2, func3):
        if piece.is_empty_piece():
            return
        threaten_piece = copy(piece)
        threaten_piece.init_threaten_piece(pos)
        way = threaten_piece.belongto
        if not only:
            cls.handle_rock_line(game, pos, func2)
            
        if threaten_piece.id == 'r':
            cls.handle_rock_threaten(game, threaten_piece, pos, func1)
            if not only:
                cls.handle_rock_king(game, pos, func3)
                cls.handle_middle(game, threaten_piece.belongto, pos, func1, func3)
            return
        
        now_id = 'g' if threaten_piece.promoted else threaten_piece.id
        for reachable in MOVEMENT[now_id]:
            _reachable = copy(reachable)
            _reachable.rotate(way)
            new_pos = pos + _reachable
            func1(game, new_pos, threaten_piece)

        if only:
            return

        if threaten_piece.id == 'k':
            cls.handle_blocker_king(game, threaten_piece.belongto, pos, func1, func3)
        else:
            cls.handle_middle(game, threaten_piece.belongto, pos, func1, func3)

    @classmethod
    def create_threaten(cls, game, piece, pos, only=False):
        cls.handle_threaten(game, piece, pos, only, cls.add_piece_to_set, cls.discard_piece_to_set, cls.remove_threaten)

    @classmethod
    def remove_threaten(cls, game, piece, pos, only=False):
        cls.handle_threaten(game, piece, pos, only, cls.discard_piece_to_set, cls.add_piece_to_set, cls.create_threaten)