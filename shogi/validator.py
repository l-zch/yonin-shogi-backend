from .position import Position
from .piece import MOVEMENT
from copy import copy

class Validator:
    
    @classmethod
    def is_vaild_place(cls, game, piece, from_pos, new_pos) -> bool:
        # 檢查持駒or移動合法 f
        # 打步詰 f
        # 二步 f
        # 打入位置合法 f
        # 新位置若有棋非己方棋才可移動過去 f
        # 若升變，升變是否合法
        #vaildate pos
        if not from_pos.is_vaild_pos() and not from_pos.is_empty_pos():
            return False
        if not new_pos.is_vaild_pos():
            return False
        if game.piece_at(new_pos).belongto == game.current_player.id:
            return False
        if game.piece_at(new_pos).id == 'k':
            return False
        if from_pos.is_empty_pos():
            return cls.is_vaild_drop(game, piece, new_pos)
        else:
            return cls.is_vaild_movement(game, piece, from_pos, new_pos)

    @staticmethod
    def is_vaild_movement(game, piece, from_pos, new_pos):
        if game.piece_at(from_pos).is_empty_piece():
                return False
        from_piece = game.piece_at(from_pos)
        if (from_piece.belongto != piece.belongto or
                #from_piece.promoted != piece.promoted or
                from_piece.id != piece.id):
            return False
        if from_piece.promoted != piece.promoted:
            if from_piece.promoted:
                return False

        facing = game.current_player.id
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
        if not find:
            return False
        if from_piece.id != 'r':
            return find
        tmp_pos = copy(from_pos) + delta_pos
        while tmp_pos != new_pos:
            if not game.piece_at(tmp_pos).is_empty_piece():
                find = False
            tmp_pos += delta_pos
        return find

    @classmethod
    def is_vaild_drop(cls, game, piece, new_pos, blocker = False):
        if not game.piece_at(new_pos).is_empty_piece():
            return False
        left_in_hand = game.current_player.holding_piece[piece.id]
        if not left_in_hand or left_in_hand <= 0:
            return False
        if piece.promoted:
            return False
        if piece.id != 'p':
            return True
        facing = game.current_player.id
        if not cls.is_vaild_drop_pawn(game, new_pos, facing):
            return False
        unit_forward = Position(-1, 0)
        unit_forward.rotate(facing)
        forward_pos = new_pos + unit_forward
        forward_ch = game.piece_at(forward_pos)
        if forward_ch.id == 'k' and forward_ch.belongto != facing and not blocker:  #打步詰
            return not game.is_checkmated(new_pos, game.players[forward_ch.belongto])
        else:
            return True

    @staticmethod
    def is_vaild_drop_pawn(game, new_pos, facing):
        if facing % 2 == 0:
            if ((new_pos.x == 0 and facing == 0)
            or (new_pos.x == 8 and facing == 2)):
                return False
            for row in range(9):
                ch = game.board[row][new_pos.y]
                if ch.belongto == facing and ch.id == 'p':
                    return False
        else:
            if ((new_pos.y == 8 and facing == 1)
            or (new_pos.y == 0 and facing == 3)):
                return False
            for col in range(9):
                ch = game.board[new_pos.x][col]
                if ch.belongto == facing and ch.id == 'p':
                    return False
        return True

    