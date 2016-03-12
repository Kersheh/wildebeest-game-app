from flask import Flask, jsonify
import wildebeest_board_generator
gen = wildebeest_board_generator

app = Flask(__name__, static_url_path="/static")

# index page routing
@app.route("/")
@app.route("/index.html")
def index():
  return open("static/index.html").read()

# player move
@app.route("/api/v1.0/<string:move>", methods=["GET"])
def get_query(move):
  coords = move.split("x")
  # check api call
  if len(coords) is 2:
    try:
      int(coords[0])
      if coords[0] >= 0 or coords[0] <= 10:
        try:
          int(coords[1])
          if coords[1] >= 0 or coords[1] <= 10:
            # do work here
            pass
        except:
          print "Invalid api call to move piece."
    except:
      print "Invalid api call to move piece."
  else:
    print "Invalid api call to move piece."

def jsonify_board(board):
  board = [["." for i in range(11)] for j in range(11)]
  board[3][1] = "*"
  board[3][9] = "*"
  board[5][5] = "#"
  board[7][1] = "*"
  board[7][9] = "*"
  for piece in self.pieces:
      board[piece.x][piece.y] = piece.id
  return json_board

def init_board():
  return gen.load_board("board")

if __name__ == "__main__":
  board = init_board()
  #app.run(host="192.168.2.156", port=5000)
  app.run()