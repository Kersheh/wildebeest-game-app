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
  board = init_board()
  print "-- NEW GAME --"
  print board
  return json.dumps(board, default=lambda o: o.__dict__)
  return jsonify_board(board)

# player move
@app.route("/api/v1.0/move/<string:move>", methods=["POST"])
def get_move(move):
  client_board = request.get_json(silent=True)
  board = new_board_object(client_board)
  coords = move.split("x")
  # check api call
  if len(coords) == 4:
    try:
      for i in range(4):
        if int(coords[i]) < 0 or int(coords[i]) > 10:
          abort(400)
        # player is white, check if move is a black piece
        if board.get_piece(int(coords[0]), int(coords[1])) in gen.BLACK_ID:
          abort(400)
      new_board = board.move_piece(int(coords[0]), int(coords[1]), int(coords[2]), int(coords[3]))
      if new_board is not None:
        board = new_board
        print "Human Player:"
        print board
        return json.dumps(board, default=lambda o: o.__dict__)
      else:
        abort(400)
    except:
      abort(400)
  else:
    abort(400)

# AI move
@app.route("/api/v1.0/move/ai", methods=["POST"])
def get_move_ai():
  client_board = request.get_json(silent=True)
  board = new_board_object(client_board)
  moves = []
  for move in board.possible_moves():
    moves.append(Move(move))
  # sort boards based on score and output best score
  moves.sort(key=lambda x: x.score, reverse=True)
  board = moves[0].board
  print "AI Player:"
  print board
  return json.dumps(board, default=lambda o: o.__dict__)

# initial the board based on server file
def init_board():
  return gen.load_board("boards/board")

def new_board_object(json):
  pieces = []
  for json_piece in json["pieces"]:
    piece_id = str(json_piece["id"])
    x = int(json_piece["x"])
    y = int(json_piece["y"])
    pieces.append(gen.Piece(piece_id, x, y))
  board = gen.Wildebeest(json["player_turn"], pieces, 0, 0, 0)
  return board

## An instance of a state  
class Move:
    HEUR_VAL = {
        "K": 1000, "W": 1000, "E": 150, "G": 100,
        "S": 120, "O": 20, "J": 110, "C": 100, 
        "X": 40, "H": 10, "Z": 50, "P": 10, 
        "B": 30, "N": 40, "R": 60
    }

    def __init__(self, board, depth=2):
        self.board = board
        self.score = self.max(board, depth, -1000000, 1000000)

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
        friendly_pieces = {}
        enemy_pieces = {}
        # value pieces and store friendly/enemy pieces in lists
        for piece in self.board.pieces:
            # black's turn, therefore calculate the move white made
            if self.board.player_turn == "B":
                if piece.id.isupper():
                    friendly_pieces[piece.id.upper()] = piece
                    score += Move.HEUR_VAL[piece.id.upper()]
                if piece.id.islower():
                    enemy_pieces[piece.id.upper()] = piece
                    score -= Move.HEUR_VAL[piece.id.upper()]
            # white's turn, therefore calculate the move black made
            if self.board.player_turn == "W":
                if piece.id.islower():
                    friendly_pieces[piece.id.upper()] = piece
                    score += Move.HEUR_VAL[piece.id.upper()]
                if piece.id.isupper():
                    enemy_pieces[piece.id.upper()] = piece
                    score -= Move.HEUR_VAL[piece.id.upper()]
        # add points for better catapult positioning
        if "C" in friendly_pieces:
            if friendly_pieces["C"].x != 0 and friendly_pieces["C"].x != 10:
                score += 100
        return score

    # max / min with alpha beta pruning
    def max(self, board, depth, alpha, beta):
        if depth == 0:
            return self.heuristic(board)
        for move in board.possible_moves():
            score = self.min(move, depth - 1, alpha, beta)
            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
        return alpha

    def min(self, board, depth, alpha, beta):
        if depth == 0:
            return self.heuristic(board)
        for move in board.possible_moves():
            score = self.max(move, depth - 1, alpha, beta)
            if score <= alpha:
                return alpha
            if score < beta:
                beta = score
        return beta

if __name__ == "__main__":
  board = init_board()
  #app.run(host="192.168.2.156", port=5000)
  app.run()