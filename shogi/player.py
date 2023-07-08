class Player:

    def __init__(self, id):
        self.id = id
        self.holding_piece = {'p':0, 's':0, 'g':0, 'r':0}
        self.checkmated = False
        self.king_pos = None