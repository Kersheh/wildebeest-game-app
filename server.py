import json
from flask import Flask, jsonify, abort, request
import lib.wildebeest_board_generator, lib.wildebeest_ai

gen = lib.wildebeest_board_generator
ai = lib.wildebeest_ai
app = Flask(__name__, static_url_path="/static")

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
        if board.get_piece(int(coords[0]), int(coords[1])).id in gen.BLACK_ID:
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

# ai move
@app.route("/api/v1.0/move/ai", methods=["POST"])
def get_move_ai():
  client_board = request.get_json(silent=True)
  board = new_board_object(client_board)
  moves = []
  for move in board.possible_moves():
    moves.append(ai.Move(move))
  # sort boards based on score and output best score
  moves.sort(key=lambda x: x.score, reverse=True)
  board = moves[0].board
  print "AI Player:"
  print board
  return json.dumps(board, default=lambda o: o.__dict__)

# initial the board based on server file
def init_board():
  return gen.load_board("boards/board")

# generate new Wildebeest object based on given json
def new_board_object(json):
  pieces = []
  for json_piece in json["pieces"]:
    piece_id = str(json_piece["id"])
    x = int(json_piece["x"])
    y = int(json_piece["y"])
    pieces.append(gen.Piece(piece_id, x, y))
  board = gen.Wildebeest(json["player_turn"], pieces, 0, 0, json["move_count"] + 1)
  return board

if __name__ == "__main__":
  #app.run(host="192.168.2.156", port=5000)
  app.run()