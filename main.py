'''from shogi.game import Game
from shogi.utils import Position
import os
g = Game()



print_board()

while True:
    try:
        #print(f"It's player {g.current_player.id}'s turn!")
        #move_type = int(input())
        if True: #move_type == 1:#move from exist piece
            player_id, from_x, from_y, to_x, to_y = map(int, input().split())
            g.current_player = g.players[player_id]
            piece = g.board[from_x][from_y]
            g.on_place(piece, Position(from_x, from_y), Position(to_x, to_y))
            print_board()
    except Exception as error:
        #os.system('clear')
        print(str(error))
'''


from shogi.game import Game
from shogi.piece import Piece
from shogi.utils import Position
import os

g = Game()

def print_board(board):
    # os.system('clear')
    for i in range(9):
        print(i, end='')
    print()
    for i in range(9):
        for j in range(9):
            if not board[i][j].is_empty_piece():
                print(board[i][j].id, end='')
            else:
                print('-', end='')
        print('')


from socketio import AsyncServer, AsyncNamespace
from sanic import Sanic
from sanic_cors import CORS
from itertools import chain
from sanic.response import text
from copy import deepcopy

sio = AsyncServer(
    async_mode='sanic',
    cors_allowed_origins=[],
    # logger=True,
    # engineio_logger=True
)


app = Sanic(name=__name__)
CORS(app)
app.config['CORS_SUPPORTS_CREDENTIALS'] = True
# app.debug = True
sio.attach(app)


@app.get("/")
def main(request):
    return text("https://tseng-chen.github.io/yonin-shogi/")


def convert(piece):
    if piece.is_empty_piece():
        return -1
    if piece.promoted:
        return {'p': 5, 's': 6, 'r': 7}[piece.id]
    return {'p': 0, 's': 1, 'g': 2, 'r': 3, 'k': 4}[piece.id]


def create_response(game):
    pieces = list(chain(*[row for row in game.board]))
    return [
        [{
        'type': convert(piece),
        'owner': piece.belongto
    } for piece in pieces],
        [{'piecesInHand': list(player.holding_piece.values())} for player in game.players],
        game.current_player.id
    ]


class NameSpace(AsyncNamespace):

    async def on_join(self, sid):
        game = Game()
        async with self.session(sid) as session:
            session['game'] = game
        await self.emit('update', create_response(game), room=sid)

    async def on_move(self, sid, data):
        session = await self.get_session(sid)
        game = session.get('game')
        
        origin, destination, promotion = data
        x, y = origin
        piece = deepcopy(game.board[x][y])
        piece.promoted = promotion
        # move the piece
        if game.on_place(piece, Position(*origin),
                         Position(*destination)):
            # if success
            await self.emit('update', create_response(game), room=sid)
        #print_board(game.board)
                             
    async def on_drop(self, sid, data):
        session = await self.get_session(sid)
        game = session.get('game')
        
        destination, piece_type = data
        piece = Piece.get_piece_num(piece_type)
        if game.on_place(piece, Position.empty_pos(),
                         Position(*destination)):
            # if success
            await self.emit('update', create_response(game), room=sid)
        #print_board(game.board)
# [
#     [Piece ... {type:Number, owner:Number}],
#     [Player ... { id:Number, piecesInHand:[count_type_0, count_type_1 ...] } ]
# ]

namespace = NameSpace('/game')
sio.register_namespace(namespace)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)