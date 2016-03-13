import json
from flask import Flask, jsonify, abort
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
  global board
  board = init_board()
  return jsonify_board(board)

# current board
@app.route("/api/v1.0/board", methods=["GET"])
def get_board():
  return jsonify_board(board)

# player move
@app.route("/api/v1.0/move/<string:move>", methods=["GET"])
def get_move(move):
  global board
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
@app.route("/api/v1.0/move/ai", methods=["GET"])
def get_move_ai():
  global board
  for move in board.possible_moves():
    return jsonify_board(move)

def is_move_valid(x, y, new_x, new_y):
  global board
  friendly_pieces = gen.WHITE_ID if board.player_turn is "W" else gen.BLACK_ID
  coords = board.legal_piece_coordinates(board.get_piece(x, y), friendly_pieces)
  for move in coords:
    if move[0] is new_x and move[1] is new_y:
      return True
  return False

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

def init_board():
  return gen.load_board("board")

if __name__ == "__main__":
  board = init_board()
  #app.run(host="192.168.2.156", port=5000)
  app.run()