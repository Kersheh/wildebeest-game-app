import wildebeest_board_generator
gen = wildebeest_board_generator

## An instance of a state  
class Move:
  HEUR_VAL = {
    "K": 10000, "W": 10000, "E": 150, "G": 100,
    "S": 120, "O": 20, "J": 110, "C": 100, 
    "X": 40, "H": 10, "Z": 50, "P": 10, 
    "B": 30, "N": 40, "R": 60
  }

  def __init__(self, board, depth=1):
    self.board = board
    if board.move_count < 10 or board.elapsed_time > board.total_time / 2:
      depth = 0
    self.score = self.max(board, depth, self.heuristic(board), 1000000)

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

  # determines manhattan distance to enemy king based on piece value multiplier
  def manhattan_to_king(self, piece, friendly, enemy):
    score = 0
    if piece in friendly:
      if "K" in enemy:
        score += 100 - abs(enemy["K"].x - friendly[piece].x) * 10
        score += 100 - abs(enemy["K"].y - friendly[piece].y) * 10
      if "W" in enemy:
        score += 100 - abs(enemy["W"].x - friendly[piece].x) * 10
        score += 100 - abs(enemy["W"].y - friendly[piece].y) * 10
    try:
      score = score * (Move.HEUR_VAL[piece] / 100)
    except:
      pass
    return score

  # generates heuristic score based on board state
  def heuristic(self, board):
    score = 0
    friendly_pieces = {}
    enemy_pieces = {}
    # value pieces and store friendly/enemy pieces in lists
    for piece in board.pieces:
      # black's turn, therefore calculate the move white made
      if board.player_turn == "B":
        if piece.id.isupper():
          friendly_pieces[piece.id.upper()] = piece
          score += Move.HEUR_VAL[piece.id.upper()]
        if piece.id.islower():
          enemy_pieces[piece.id.upper()] = piece
          score -= Move.HEUR_VAL[piece.id.upper()]
      # white's turn, therefore calculate the move black made
      if board.player_turn == "W":
        if piece.id.islower():
          friendly_pieces[piece.id.upper()] = piece
          score += Move.HEUR_VAL[piece.id.upper()]
        if piece.id.isupper():
          enemy_pieces[piece.id.upper()] = piece
          score -= Move.HEUR_VAL[piece.id.upper()]

    ## hardcoded starting moves
    # move joey as first move
    if board.move_count == 1 or board.move_count == 2:
      if "J" in friendly_pieces:
        if friendly_pieces["J"].x == 2 or friendly_pieces["J"].x == 8:
          score += 10000
    if board.move_count == 3 or board.move_count == 4:
      if "P" in friendly_pieces:
        if friendly_pieces["P"].y == 8 and friendly_pieces["P"].y == 8:
          if friendly_pieces["P"].x == 2 or friendly_pieces["P"].x == 8:
            score += 10000

    ## offensive points
    # add points for better catapult positioning
    if "C" in friendly_pieces:
      if friendly_pieces["C"].x == 1 or friendly_pieces["C"].x == 9:
        score += 500
      if friendly_pieces["C"].x == 2 or friendly_pieces["C"].x == 8:
        score += 1000

    test = 0
    # add points moving empress to enemy king
    score += self.manhattan_to_king("E", friendly_pieces, enemy_pieces)
    # add points moving serpent to enemy king
    score += self.manhattan_to_king("S", friendly_pieces, enemy_pieces)
    # add points moving rook to enemy king
    score += self.manhattan_to_king("R", friendly_pieces, enemy_pieces)
    # add points moving bishop to enemy king
    score += self.manhattan_to_king("B", friendly_pieces, enemy_pieces)
    # add points moving gorilla to enemy king
    score += self.manhattan_to_king("G", friendly_pieces, enemy_pieces)
    return score

  # max with alpha beta pruning
  def max(self, board, depth, alpha, beta):
    if depth == 0:
      return self.heuristic(board)
    for move in board.possible_moves():
      score = self.min(move, depth - 1, alpha, beta)
      if score > beta:
        return beta
      if score > alpha:
        alpha = score
    return alpha

  # min with alpha beta pruning
  def min(self, board, depth, alpha, beta):
    if depth == 0:
      return self.heuristic(board) * (-1)
    for move in board.possible_moves():
      score = self.max(move, depth - 1, alpha, beta)
      if score <= alpha:
        return alpha * (-1)
      if score < beta:
        beta = score
    return beta * (-1)