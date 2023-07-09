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
    def handle_rock_line(game, threaten_piece, pos, func2):
        #handle blocking or unblocking rock range line
        for piece_r in game.threaten_piece_at(pos):
            if piece_r.id == 'r':
                unit_way = Position.get_unit_way(piece_r.pos, pos)
                new_pos = pos + unit_way
                while new_pos.is_vaild_pos():
                    func2(new_pos, piece_r)
                    game.threaten_piece_at(new_pos).discard(piece_r)
                    if not game.piece_at(new_pos).is_empty_piece():
                        break
                    new_pos += unit_way

    @staticmethod
    def handle_rock_threaten(game, threaten_piece, pos, func1):
        if threaten_piece.promoted:
            for reachable in MOVEMENT['R']:
                new_pos = pos + reachable
                func1(new_pos, threaten_piece)
        for w in MOVEMENT['r']:
            new_pos = pos + w
            while new_pos.is_vaild_pos():
                func1(new_pos, threaten_piece)
                if not game.piece_at(new_pos).is_empty_piece():
                    break
                new_pos += w

    @classmethod
    def handle_rock_king(cls, game, pos):
        #if a king in a row or a col
        for player in game.players:
            if player.id == game.current_player.id:
                continue
            kp = player.king_pos
            if kp.x == pos.x:
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
                    cls.remove_threaten(blockers[0], blockers[0].pos, True)
            elif kp.y == pos.y:
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
                    cls.remove_threaten(blockers[0], blockers[0].pos, True)

    @classmethod
    def handle_blocker(cls, game, threaten_piece, pos, func1):
        for unit_way in MOVEMENT['r']:
            new_pos = pos + unit_way
            blockers = []
            while new_pos.is_vaild_pos():
                ch = game.piece_at(new_pos)
                if ch.id == 'r' and ch.belongto != threaten_piece.belongto:
                    if len(blockers) != 1:
                        break
                    if blockers[0].belongto == threaten_piece.belongto:
                        cls.remove_threaten(blockers[0], blockers[0].pos, True)
                        two_way = [unit_way, unit_way * -1]
                        for w in two_way:
                            if w in MOVEMENT[blockers[0].id]:
                                func1(blockers[0].pos + w, blockers[0])
                    break
                elif not ch.is_empty_piece():
                    _ch = copy(ch)
                    _ch.init_threaten_piece(new_pos)
                    blockers.append(_ch)
                new_pos += unit_way

    @classmethod
    def handle_threaten(cls, game, piece, pos, only, func1, func2):
        if piece.is_empty_piece():
            return
        threaten_piece = copy(piece)
        threaten_piece.init_threaten_piece(pos)
        way = threaten_piece.belongto
        if not only:
            cls.handle_rock_line(game, threaten_piece, pos, func2)
            
        if threaten_piece.id == 'r':
            cls.handle_rock_threaten(game, threaten_piece, pos, func1)
            if not only:
                cls.handle_rock_king(game, pos)
            return
        
        now_id = 'g' if threaten_piece.promoted else threaten_piece.id
        for reachable in MOVEMENT[now_id]:
            _reachable = copy(reachable)
            _reachable.rotate(way)
            new_pos = pos + _reachable
            func1(game, new_pos, threaten_piece)

        if threaten_piece.id == 'k':
            cls.handle_blocker(game, threaten_piece, pos, func1)

    @classmethod
    def create_threaten(cls, game, piece, pos, only=False):
        cls.handle_threaten(piece, pos, only, game.add_piece_to_set, game.discard_piece_to_set)

    @classmethod
    def remove_threaten(cls, game, piece, pos, only=False):
        cls.handle_threaten(piece, pos, only, game.discard_piece_to_set, game.add_piece_to_set)