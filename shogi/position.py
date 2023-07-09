class Position:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __add__(self, other):
        return Position(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Position(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return Position(self.x * other, self.y * other)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self

    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y
        return self

    def rotate(self, n):
        if n == 1:
            self.x, self.y = self.y, -self.x
        elif n == 2:
            self.x, self.y = -self.x, -self.y
        elif n == 3:
            self.x, self.y = -self.y, self.x

    def is_empty_pos(self):
        return self.x == -10 and self.y == -10

    def is_vaild_pos(self):
        return all([0 <= self.x, self.x <= 8, 0 <= self.y, self.y <= 8])

    @classmethod
    def empty_pos(cls):
        return cls(-10, -10)

    #return unit vector or return original pos if 
    def get_unit_way(from_pos, to_pos):
        d = to_pos - from_pos
        if d.x != 0 and d.y != 0:
            return d
        if d.x == 0:
            if d.y > 0:
                return Position(0,1)
            else:
                return Position(0,-1)
        elif d.x > 0:
            return Position(1,0)
        else:
            return Position(-1,0)

    def __str__(self):
        return "x=" + str(self.x) + ",y=" + str(self.y)

#NON_POS = Position(-1, -1)