import json
from flask import Flask, jsonify, abort, request
import wildebeest_board_generator
gen = wildebeest_board_generator

app = Flask(__name__, static_url_path="/static")
board = []

# index page routing
@app.route("/")
@app.route("/index.html")
def index():
  return open("static/index.html").read()

# reset board
@app.route("/api/v1.0/board/reset", methods=["GET"])
def reset_board():
  return jsonify_board(init_board())

# player move
@app.route("/api/v1.0/move/<string:move>", methods=["POST"])
def get_move(move):
  client_board = request.get_json(silent=True)
  board = deserialize_board(client_board)
  coords = move.split("x")
  # check api call
  if len(coords) is 4:
    try:
      for i in range(4):
        if int(coords[i]) < 0 or int(coords[i]) > 10:
          abort(400)
      new_board = board.move_piece(int(coords[0]), int(coords[1]), int(coords[2]), int(coords[3]))
      if new_board is not None:
        board = new_board
        return jsonify_board(board)
      else:
        abort(400)
    except:
      abort(400)
  else:
    abort(400)

# AI move
@app.route("/api/v1.0/move/ai", methods=["POST"])
def get_move_ai():
  client_board = json.dumps(request.get_json(silent=True))
  board = deserialize_board(client_board)
  moves = []
  for move in board.possible_moves():
    moves.append(Move(move))
  # sort boards based on score and output best score
  moves.sort(key=lambda x: x.score, reverse=True)
  board = moves[0].board
  return jsonify_board(moves[0].board)

# package board into json for api response
def jsonify_board(board):
  result = {"player_turn": board.player_turn}
  json_board = [[" " for i in range(11)] for j in range(11)]
  json_board[3][1] = "*"
  json_board[3][9] = "*"
  json_board[5][5] = "#"
  json_board[7][1] = "*"
  json_board[7][9] = "*"
  for piece in board.pieces:
    json_board[piece.x][piece.y] = piece.id
  result["board"] = json_board
  return json.dumps(result)

# initial the board based on server file
def init_board():
  return gen.load_board("board")

def deserialize_board(json):
  pieces = []
  for i in range(11):
    for j in range(11):
      if json["board"][i][j] in gen.WHITE_ID or \
         json["board"][i][j] in gen.BLACK_ID:
        pieces.append(gen.Piece(json["board"][i][j], i, j))
  test = [gen.Piece("Z", 0, 0)]
  # can't figure out why the object isn't being generated
  print "test"
  print gen.Wildebeest("W", gen.Piece("R", 0, 0), 0, 0, 0)
  print gen.Wildebeest(json["player_turn"], pieces, 0, 0, 0)
  return gen.Wildebeest(json["player_turn"], pieces, 0, 0, 0)

DEPTH = 1
## An instance of a state  
class Move:
    HEUR_VAL = {
        "K": 500, "W": 500, "E": 150, "G": 100,
        "S": 120, "O": 20, "J": 110, "C": 100, 
        "X": 40, "H": 10, "Z": 50, "P": 10, 
        "B": 30, "N": 40, "R": 60
    }

    def __init__(self, board):
        self.board = board
        self.score = self.max(board, DEPTH)

    def __eq__(self, other):
        return self.__repr__() == other.__repr__()

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.__repr__())

    def __repr__(self):
        s = "{0}".format(self.score) + "\n"
        s += "{0}".format(self.board)
        return s

    def heuristic(self, board):
        score = 0
        for piece in self.board.pieces:
            # black's turn, calculate white's move
            if self.board.player_turn is "B":
                if piece.id.isupper():
                    score += Move.HEUR_VAL[piece.id.upper()]
                if piece.id.islower():
                    score -= Move.HEUR_VAL[piece.id.upper()]
            # white's turn, calculate black's move
            if self.board.player_turn is "W":
                if piece.id.islower():
                    score += Move.HEUR_VAL[piece.id.upper()]
                if piece.id.isupper():
                    score -= Move.HEUR_VAL[piece.id.upper()]
        return score

    def max(self, board, depth):
        if depth is 0:
            return self.heuristic(board)
        bestScore = -1000000
        for move in board.possible_moves():
            score = self.min(move, depth - 1)
            if score > bestScore:
                bestScore = score
                bestMove = move
        return bestScore

    def min(self, board, depth):
        if depth is 0:
            return self.heuristic(board)
        worstScore = 1000000
        for move in board.possible_moves():
            score = self.max(move, depth - 1)
            if score < worstScore:
                worstScore = score
                worstMove = move
        return worstScore

if __name__ == "__main__":
  board = init_board()
  #app.run(host="192.168.2.156", port=5000, threaded=True)
  app.run(threaded=True)