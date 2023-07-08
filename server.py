from socketio import AsyncServer, AsyncNamespace
from sanic import Sanic
from sanic_cors import CORS
from shogi.game import Game
from shogi.piece import Piece
from shogi.utils import Position
from itertools import chain
from sanic.response import text


sio = AsyncServer(async_mode='sanic',
                  cors_allowed_origins=[],
                  logger=True,
                  engineio_logger=True)

app = Sanic(name=__name__)
CORS(app)
app.config['CORS_SUPPORTS_CREDENTIALS'] = True
# app.debug = True
sio.attach(app)


@app.get("/")
def main(request):
    return text("hi")

game = Game()


def convert(piece):
    if piece.promoted:
        return {'p':0, 's':1, 'g':2, 'r':3 , 'k':4}[piece.id]
    return {'p':5, 's':6, 'r': 3}[piece.id]

class NameSpace(AsyncNamespace):

    async def on_move(self, sid, data):
        #origin, destination, piece_type
        piece = Piece.get_piece_num(data.piece_type)
        # move the piece
        if game.on_place(piece, Position(*data.origin), Position(*data.destination)):
            # if success
            pieces = list(chain(*game.board))
            response = [[{'type':convert(piece), 'owner':piece.belong_to} for piece in pieces],
             [{'id':player.id, 'piecesInHand':list(player.holding_piece.value()) } for player in  game.players ]]
            self.emit('update',response, room=sid)

# [
#     [Piece ... {type:Number, owner:Number}],
#     [Player ... { id:Number, piecesInHand:[count_type_0, count_type_1 ...] } ]
# ]

namespace = NameSpace('/game')
sio.register_namespace(namespace)
app.run(host="0.0.0.0", port=8080)