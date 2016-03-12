import json
from flask import Flask, jsonify
import wildebeest_board_generator
gen = wildebeest_board_generator

app = Flask(__name__, static_url_path="/static")
board = []

# index page routing
@app.route("/")
@app.route("/index.html")
def index():
  return open("static/index.html").read()

# current board
@app.route("/api/v1.0/board", methods=["GET"])
def get_board():
  return jsonify_board(board)

# player move
@app.route("/api/v1.0/<string:move>", methods=["GET"])
def get_move(move):
  return jsonify_board(init_board())
  coords = move.split("x")
  # check api call
  if len(coords) is 2:
    try:
      int(coords[0])
      if coords[0] >= 0 or coords[0] <= 10:
        try:
          int(coords[1])
          if coords[1] >= 0 or coords[1] <= 10:
            # process move here
            pass
        except:
          print "Invalid api call to move piece."
    except:
      print "Invalid api call to move piece."
  else:
    print "Invalid api call to move piece."

def jsonify_board(board):
  json_board = [["." for i in range(11)] for j in range(11)]
  json_board[3][1] = "*"
  json_board[3][9] = "*"
  json_board[5][5] = "#"
  json_board[7][1] = "*"
  json_board[7][9] = "*"
  for piece in board.pieces:
    json_board[piece.x][piece.y] = piece.id
  return json.dumps(json_board)

def init_board():
  return gen.load_board("board")

if __name__ == "__main__":
  board = init_board()
  #app.run(host="192.168.2.156", port=5000)
  app.run()