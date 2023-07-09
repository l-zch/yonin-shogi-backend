from .position import Position
from copy import copy

def make_position_list(*args):
  return [Position(*arg) for arg in args]


MOVEMENT = {
    'p':make_position_list((-1,0)),
    'g':make_position_list((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,0)),
    's':make_position_list((-1,-1),(-1,0),(-1,1),(1,-1),(1,1)),
    'n':make_position_list((-2,-1),(-2,1)),
    'l':make_position_list((-1,0)),
    'r':make_position_list((-1,0),(0,-1),(0,1),(1,0)),
    'R':make_position_list((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)),
    'b':make_position_list((-1,-1),(-1,1),(1,-1),(1,1)),
    'B':make_position_list((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)),
    'k':make_position_list((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1))
}
# [-1][-1] [-1][0] [-1][1]
# [0][-1]  [0][0]  [0][1]
# [1][-1]  [1][0]  [1][1]
INITIAL_BOARD = [('s', -2, 0), ('g', -1, 0), ('p', -1, 1), ('p', 0, 2), ('r', 0, 1), ('g', 1, 0), ('p', 1, 1), ('s', 2, 0)]



class Piece:

    #步 香 桂 銀 金 角 飛 王(p~k)
    def __init__(self, id):
        self.id = id
        self.promoted = False
        self.belongto = -1
        self.pos = None#debug

    def init_threaten_piece(self, pos):
        self.pos = copy(pos)

    def is_empty_piece(self):
        return self.id == 'None'

    @classmethod
    def empty_piece(cls):
        ret = cls('None')
        return ret

    @classmethod
    def get_piece_num(cls, id):
        MAP = {
            0:'p',
            1:'s',
            2:'g',
            3:'r',
            4:'k',
            5:'p',
            6:'s',
            7:'r',
        }
        ret = cls(MAP[id])
        if id >= 5:
            ret.promoted = True
        return ret

    def __eq__(self, other):
        return all([
            isinstance(other, self.__class__),
            other.id == self.id,
            other.promoted == self.promoted,
            other.belongto == self.belongto,
            other.pos == self.pos])

    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        if self.pos is not None:#
            return "id=" + self.id + ",promoted=" + str(self.promoted) + ",belongto=" + str(self.belongto) + ",pos=" + str(self.pos)#
        return "id=" + self.id + ",promoted=" + str(self.promoted) + ",belongto=" + str(self.belongto)