#!/usr/bin/python

import sys, os, subprocess, fileinput

WHITE_ID = { "S", "O", "E", "J", "C", "G", "X", "H", "Z", "K", "W", "P", "B", "N", "R" }
BLACK_ID = { "s", "o", "e", "j", "c", "g", "x", "h", "z", "k", "w", "p", "b", "n", "r" }
BIO_ID = { "S", "s", "O", "o", "E", "e", "J", "j", "G", "g", "Z", "z", "K", "k", "W", "w", "P", "p", "B", "b", "N", "n", "R", "r" }

## An instance of a piece in Wildebeest
class Piece(object):
    def __init__(self, piece_id, x, y):
        self.id = piece_id
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.__repr__())

    def __repr__(self):
        return "Piece({0}, {1}, {2})".format(self.id, self.x, self.y)

## An instance of a board of Wildebeeest
class Wildebeest(object):
    def __init__(self, player_turn, pieces, elapsed_time, total_time, move_count):
        self.player_turn = player_turn
        self.pieces = pieces
        self.elapsed_time = elapsed_time
        self.total_time = total_time
        self.move_count = move_count

    def __eq__(self, other):
        return self.__repr__() == other.__repr__()

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.__repr__())

    def __repr__(self):
        s = self.player_turn + "\n"
        board = self.get_board()
        for line in board:
            for tile in line:
                s += "{0}".format(tile)
            s += "\n"
        s += "{0}\n".format(self.elapsed_time)
        s += "{0}\n".format(self.total_time)
        s += "{0}\n".format(self.move_count)
        return s

    # return board as 2D array
    def get_board(self):
        board = [["." for i in range(11)] for j in range(11)]
        board[3][1] = "*"
        board[3][9] = "*"
        board[5][5] = "#"
        board[7][1] = "*"
        board[7][9] = "*"
        for piece in self.pieces:
            board[piece.x][piece.y] = piece.id
        return board

    # checks if piece is paralyzed
    def is_paralyzed(self, piece):
        board = self.get_board()
        if piece.id in WHITE_ID:
            friendly_pieces = WHITE_ID
            enemy_pieces = BLACK_ID
        else:
            friendly_pieces = BLACK_ID
            enemy_pieces = WHITE_ID

        for i in range(-1, 2):
            for j in range(-1, 2):
                # skip out-of-bounds coordinates
                if piece.x + i < 0 or piece.x + i > 10 or \
                   piece.y + j < 0 or piece.y + j > 10:
                    continue
                if board[piece.x + i][piece.y + j] in enemy_pieces:
                    if board[piece.x + i][piece.y + j] == "Z" or \
                       board[piece.x + i][piece.y + j] == "z":
                        return True
        return False

    # returns list of coordinates a piece can move based on its current location
    # note: accounts for collision with friendly pieces
    def legal_piece_coordinates(self, piece, friendly_pieces):
        board = self.get_board()
        coordinates = []

        # catapult flings piece (can fling paralyzed piece, comes before Beekeeper check)
        if piece.id != "H" or piece.id != "h" or \
           piece.id != "X" or piece.id != "x":
            for i in range(-1, 2):
                for j in range(-1, 2):
                    # skip out-of-bounds coordinates
                    if piece.x + i < 0 or piece.x + i > 10 or \
                       piece.y + j < 0 or piece.y + j > 10:
                        continue
                    # skip current coordinate
                    if i == 0 and j == 0:
                        continue
                    if board[piece.x + i][piece.y + j] in friendly_pieces:
                        if board[piece.x + i][piece.y + j] == "C" or \
                           board[piece.x + i][piece.y + j] == "c":
                            # skip if catapult is paralyzed
                            if self.is_paralyzed(piece):
                                continue;
                            for m in range(2, 11):
                                if piece.x + i * m < 0 or piece.x + i * m > 10 or \
                                   piece.y + j * m < 0 or piece.y + j * m > 10:
                                    continue
                                # skip friendly pieces
                                if board[piece.x + i * m][piece.y + j * m] in friendly_pieces:
                                    continue
                                # skip king or gorilla; piece cannot land on them
                                if board[piece.x + i * m][piece.y + j * m] == "K" or \
                                   board[piece.x + i * m][piece.y + j * m] == "k" or \
                                   board[piece.x + i * m][piece.y + j * m] == "W" or \
                                   board[piece.x + i * m][piece.y + j * m] == "w" or \
                                   board[piece.x + i * m][piece.y + j * m] == "G" or \
                                   board[piece.x + i * m][piece.y + j * m] == "g":
                                    continue
                                coordinates.append((piece.x + i * m, piece.y + j * m))

        # skip piece if paralyzed by enemy Beekeeper
        if piece.id != "X" and piece.id != "x" and \
           piece.id != "H" and piece.id != "h":
            if self.is_paralyzed(piece):
                return coordinates

        # moves like a king
        if piece.id == "S" or piece.id == "s" or piece.id == "O" or piece.id == "o" or \
           piece.id == "J" or piece.id == "j" or piece.id == "C" or piece.id == "c" or \
           piece.id == "G" or piece.id == "g" or piece.id == "Z" or piece.id == "z" or \
           piece.id == "K" or piece.id == "k":
            for i in range(-1, 2):
                for j in range(-1, 2):
                    # skip out-of-bounds coordinates
                    if piece.x + i < 0 or piece.x + i > 10 or \
                       piece.y + j < 0 or piece.y + j > 10:
                        continue
                    # skip current coordinate
                    if i == 0 and j == 0:
                        continue
                    # skip gorilla; cannot capture it
                    if board[piece.x + i][piece.y + j] == "G" or \
                       board[piece.x + i][piece.y + j] == "g":
                        continue
                    # catapult cannot capture pieces
                    if piece.id == "C" or piece.id == "c":
                        if board[piece.x + i][piece.y + j] in WHITE_ID or \
                           board[piece.x + i][piece.y + j] in BLACK_ID:
                            continue
                    # skip friendly pieces (except Gorilla)
                    if piece.id != "G" and piece.id != "g":
                        if board[piece.x + i][piece.y + j] in friendly_pieces:
                            continue
                    coordinates.append((piece.x + i, piece.y + j))

        # moves like a knight
        if piece.id == "E" or piece.id == "e" or piece.id == "N" or piece.id == "n":
            for i in range(-1, 2, 2):
                for j in range(-2, 3, 4):
                    if piece.x + i < 0 or piece.x + i > 10 or \
                       piece.y + j < 0 or piece.y + j > 10:
                        pass
                    else:
                        if board[piece.x + i][piece.y + j] not in friendly_pieces:
                            # skip gorilla; cannot capture it
                            if board[piece.x + i][piece.y + j] != "G" and \
                               board[piece.x + i][piece.y + j] != "g":
                                coordinates.append((piece.x + i, piece.y + j))
                    if piece.x + j < 0 or piece.x + j > 10 or \
                       piece.y + i < 0 or piece.y + i > 10:
                        pass
                    else:
                        if board[piece.x + j][piece.y + i] not in friendly_pieces:
                            # skip gorilla; cannot capture it
                            if board[piece.x + j][piece.y + i] != "G" and \
                               board[piece.x + j][piece.y + i] != "g":
                                coordinates.append((piece.x + j, piece.y + i))

        # moves like a golf cart (uncharged)
        if piece.id == "X" or piece.id == "x":
            if piece.y != 0 and board[piece.x][piece.y - 1] not in friendly_pieces:
                # skip gorilla; cannot capture it
                if board[piece.x][piece.y - 1] != "G" and \
                   board[piece.x][piece.y - 1] != "g":
                    coordinates.append((piece.x, piece.y - 1))
            if piece.y != 10 and board[piece.x][piece.y + 1] not in friendly_pieces:
                # skip gorilla; cannot capture it
                if board[piece.x][piece.y + 1] != "G" and \
                   board[piece.x][piece.y + 1] != "g":
                    coordinates.append((piece.x, piece.y + 1))

        # moves like a bishop (cuts off when path is blocked)
        if piece.id == "W" or piece.id == "w" or piece.id == "B" or piece.id == "b" or \
           piece.id == "E" or piece.id == "e":
            up_left, up_right, down_left, down_right = True, True, True, True
            for i in range(1, 11):
                if up_left:
                    if piece.x - i < 0 or piece.y - i < 0 or \
                       board[piece.x - i][piece.y - i] in friendly_pieces:
                        up_left = False
                    else:
                        # skip gorilla; cannot capture it
                        if board[piece.x - i][piece.y - i] == "G" or \
                           board[piece.x - i][piece.y - i] == "g":
                            up_left = False
                        else:
                            coordinates.append((piece.x - i, piece.y - i))
                        # if enemy piece found, restrict further movement
                        if board[piece.x - i][piece.y - i] in WHITE_ID or \
                           board[piece.x - i][piece.y - i] in BLACK_ID:
                            up_left = False
                if up_right:
                    if piece.x - i < 0 or piece.y + i > 10 or \
                       board[piece.x - i][piece.y + i] in friendly_pieces:
                        up_right = False
                    else:
                        # skip gorilla; cannot capture it
                        if board[piece.x - i][piece.y + i] == "G" or \
                           board[piece.x - i][piece.y + i] == "g":
                            up_right = False
                        else:
                            coordinates.append((piece.x - i, piece.y + i))
                        # if enemy piece found, restrict further movement
                        if board[piece.x - i][piece.y + i] in WHITE_ID or \
                           board[piece.x - i][piece.y + i] in BLACK_ID:
                            up_right = False
                if down_left:
                    if piece.x + i > 10 or piece.y - i < 0 or \
                       board[piece.x + i][piece.y - i] in friendly_pieces:
                        down_left = False
                    else:
                        # skip gorilla; cannot capture it
                        if board[piece.x + i][piece.y - i] == "G" or \
                           board[piece.x + i][piece.y - i] == "g":
                            down_left = False
                        else:
                            coordinates.append((piece.x + i, piece.y - i))
                        # if enemy piece found, restrict further movement
                        if board[piece.x + i][piece.y - i] in WHITE_ID or \
                           board[piece.x + i][piece.y - i] in BLACK_ID:
                            down_left = False
                if down_right:
                    if piece.x + i > 10 or piece.y + i > 10 or \
                       board[piece.x + i][piece.y + i] in friendly_pieces:
                        down_right = False
                    else:
                        # skip gorilla; cannot capture it
                        if board[piece.x + i][piece.y + i] == "G" or \
                           board[piece.x + i][piece.y + i] == "g":
                            down_right = False
                        else:
                            coordinates.append((piece.x + i, piece.y + i))
                        # if enemy piece found, restrict further movement
                        if board[piece.x + i][piece.y + i] in WHITE_ID or \
                           board[piece.x + i][piece.y + i] in BLACK_ID:
                            down_right = False

        # moves like a pawn (white side)
        if piece.id == "P" and board[piece.x + 1][piece.y] not in WHITE_ID and \
           board[piece.x + 1][piece.y] not in BLACK_ID:
            if piece.x == 1 and board[piece.x + 2][piece.y] not in WHITE_ID and \
               board[piece.x + 2][piece.y] not in BLACK_ID:
                coordinates.append((piece.x + 2, piece.y))
            if piece.x != 10:
                coordinates.append((piece.x + 1, piece.y))

        # overtake enemy piece like a pawn (white side)
        if piece.id == "P" and piece.x != 10:
            for i in range(-1, 2, 2):
                if piece.y + i > 0 and piece.y + i < 11 and \
                   board[piece.x + 1][piece.y + i] != "G" and \
                   board[piece.x + 1][piece.y + i] != "g":
                    if board[piece.x + 1][piece.y + i] not in friendly_pieces:
                        if board[piece.x + 1][piece.y + i] in WHITE_ID or \
                           board[piece.x + 1][piece.y + i] in BLACK_ID:
                            coordinates.append((piece.x + 1, piece.y + i))

        # moves like a pawn (black side)
        if piece.id == "p" and board[piece.x - 1][piece.y] not in WHITE_ID and \
           board[piece.x - 1][piece.y] not in BLACK_ID:
            if piece.x == 9 and board[piece.x - 2][piece.y] not in WHITE_ID and \
               board[piece.x - 2][piece.y] not in BLACK_ID:
                coordinates.append((piece.x - 2, piece.y))
            if piece.x != 0:
                coordinates.append((piece.x - 1, piece.y))

        # overtake enemy piece like a pawn (black side)
        if piece.id == "p" and piece.x != 0:
            for i in range(-1, 2, 2):
                if piece.y + i > 0 and piece.y + i < 11 and \
                   board[piece.x - 1][piece.y + i] != "G" and \
                   board[piece.x - 1][piece.y + i] != "g":
                    if board[piece.x - 1][piece.y + i] not in friendly_pieces:
                        if board[piece.x - 1][piece.y + i] in WHITE_ID or \
                           board[piece.x - 1][piece.y + i] in BLACK_ID:
                            coordinates.append((piece.x - 1, piece.y + i))

        # moves like a rook (cuts off when path is blocked)
        if piece.id == "R" or piece.id == "r" or piece.id == "E" or piece.id == "e":
            up, right, down, left = True, True, True, True
            for i in range(1, 11):
                if up:
                    if piece.x - i < 0 or board[piece.x - i][piece.y] in friendly_pieces:
                        up = False
                    else:
                        # skip gorilla; cannot capture it
                        if board[piece.x - i][piece.y] == "G" or \
                           board[piece.x - i][piece.y] == "g":
                            up = False
                        else:
                            coordinates.append((piece.x - i, piece.y))
                        # if enemy piece found, restrict further movement
                        if board[piece.x - i][piece.y] in WHITE_ID or \
                           board[piece.x - i][piece.y] in BLACK_ID:
                            up = False
                if right:
                    if piece.y + i > 10 or board[piece.x][piece.y + i] in friendly_pieces:
                        right = False
                    else:
                        # skip gorilla; cannot capture it
                        if board[piece.x][piece.y + i] == "G" or \
                           board[piece.x][piece.y + i] == "g":
                            right = False
                        else:
                            coordinates.append((piece.x, piece.y + i))
                        # if enemy piece found, restrict further movement
                        if board[piece.x][piece.y + i] in WHITE_ID or \
                           board[piece.x][piece.y + i] in BLACK_ID:
                            right = False
                if down:
                    if piece.x + i > 10 or board[piece.x + i][piece.y] in friendly_pieces:
                        down = False
                    else:
                        # skip gorilla; cannot capture it
                        if board[piece.x + i][piece.y] == "G" or \
                           board[piece.x + i][piece.y] == "g":
                            down = False
                        else:
                            coordinates.append((piece.x + i, piece.y))
                        # if enemy piece found, restrict further movement
                        if board[piece.x + i][piece.y] in WHITE_ID or \
                           board[piece.x + i][piece.y] in BLACK_ID:
                            down = False
                if left:
                    if piece.y - i < 0 or board[piece.x][piece.y - i] in friendly_pieces:
                        left = False
                    else:
                        # skip gorilla; cannot capture it
                        if board[piece.x][piece.y - i] == "G" or \
                           board[piece.x][piece.y - i] == "g":
                            left = False
                        else:
                            coordinates.append((piece.x, piece.y - i))
                        # if enemy piece found, restrict further movement
                        if board[piece.x][piece.y - i] in WHITE_ID or \
                           board[piece.x][piece.y - i] in BLACK_ID:
                            left = False

        return coordinates

    # get Piece object belonging to board at given coordinate
    def get_piece(self, x, y):
        for piece in self.pieces:
            if piece.x == x and piece.y == y:
                return piece
        return None

    # poison effect
    def poison_effect(self, pieces):
        empress = False
        serpents = []
        for piece in pieces:
            if piece.id == "S" or piece.id == "s" or piece.id == "E" or piece.id == "e":
                serpents.append(piece)
        for piece in serpents:
            empress = False
            removed_pieces = [] # to track for empress
            for i in range(-1, 2):
                for j in range(-1, 2):
                    # skip out-of-bounds coordinates
                    if piece.x + i < 0 or piece.x + i > 10 or \
                       piece.y + j < 0 or piece.y + j > 10:
                        continue
                    # skip serpent
                    if i == 0 and j == 0:
                        continue
                    for adjacent_piece in pieces:
                        if adjacent_piece.x == piece.x + i and \
                           adjacent_piece.y == piece.y + j and \
                           adjacent_piece.id in BIO_ID:
                            if adjacent_piece.id in BLACK_ID:
                                if piece.id == "S" or piece.id == "E":
                                    removed_pieces.append(adjacent_piece)
                                    pieces.remove(adjacent_piece)
                                    if piece.id == "E":
                                        empress = True
                            if adjacent_piece.id in WHITE_ID:
                                if piece.id == "s" or piece.id == "e":
                                    removed_pieces.append(adjacent_piece)
                                    pieces.remove(adjacent_piece)
                                    if piece.id == "e":
                                        empress = True
            # check if enemy old woman transforms into grand empress from serpent
            if not empress:
                for removed_piece in removed_pieces:
                    for i in range(-1, 2):
                        for j in range(-1, 2):
                            # skip out-of-bounds coordinates
                            if removed_piece.x + i < 0 or removed_piece.x + i > 10 or \
                               removed_piece.y + j < 0 or removed_piece.y + j > 10:
                                continue
                            # skip removed piece
                            if i == 0 and j == 0:
                                continue
                            for adjacent_piece in pieces:
                                if adjacent_piece.x == removed_piece.x + i and \
                                   adjacent_piece.y == removed_piece.y + j:
                                    if piece.id == "S" and adjacent_piece.id == "o":
                                        # try block in case of two serpents removing each other
                                        try:
                                            pieces.remove(piece) # remove serpent
                                        except:
                                            pass
                                        pieces.append(Piece("e", adjacent_piece.x, adjacent_piece.y))
                                        pieces.remove(adjacent_piece)
                                    if piece.id == "s" and adjacent_piece.id == "O":
                                        # try block in case of two serpents removing each other
                                        try:
                                            pieces.remove(piece) # remove serpent
                                        except:
                                            pass
                                        pieces.append(Piece("E", adjacent_piece.x, adjacent_piece.y))
                                        pieces.remove(adjacent_piece)
        return empress

    # after effects that occur after a move is completed
    def after_effects(self, pieces):
        # initial poison
        while(self.poison_effect(pieces)):
            pass

        ## golf cart
        # golf cart (charged - time machine)
        cart_w = False
        cart_b = False
        same_column = False
        for piece in pieces:
            # white time machine
            if piece.id == "H":
                cart_w = True
            # black time machine
            if piece.id == "h": 
                cart_b = True
            # white pawn in middle (charges black golf cart)
            if piece.id == "P" and piece.x == 5:
                cart_b = True
            # black pawn in middle (charges white golf cart)
            if piece.id == "p" and piece.x == 5:
                cart_w = True
        # check both golf carts charged in the same column
        if cart_w == True and cart_b == True:
            for piece in pieces:
                if piece.id == "X":
                    cart_w_y = piece.y
                if piece.id == "x":
                    cart_b_y = piece.y
            try:
                if cart_w_y == cart_b_y:
                    same_column = True
            except:
                pass
        # white golf cart (charged)
        remove_pieces = []
        for piece in pieces:
            if piece.id == "X" and cart_w == True:
                for removed_piece in pieces:
                    if removed_piece.y == piece.y:
                        remove_pieces.append(removed_piece)
                if not same_column:
                    if piece.x == 0:
                        pieces.append(Piece(piece.id, 10, piece.y))
                    if piece.x == 10:
                        pieces.append(Piece(piece.id, 0, piece.y))
                break
        # black golf cart (charged)
        for piece in pieces:
            if piece.id == "x" and cart_b == True:
                for removed_piece in pieces:
                    if removed_piece.y == piece.y:
                        remove_pieces.append(removed_piece)
                if not same_column:
                    if piece.x == 0:
                        pieces.append(Piece(piece.id, 10, piece.y))
                    if piece.x == 10:
                        pieces.append(Piece(piece.id, 0, piece.y))
                break
        # remove pieces
        for piece in remove_pieces:
            pieces.remove(piece)

        ## transporter
        # check transporter pads for pieces
        pad = []
        for piece in pieces:
            if piece.x == 3 and piece.y == 1:
                pad.append(piece)
            if piece.x == 3 and piece.y == 9:
                pad.append(piece)
            if piece.x == 7 and piece.y == 1:
                pad.append(piece)
            if piece.x == 7 and piece.y == 9:
                pad.append(piece)
        # transport pieces
        for piece in pad:
            if piece.x == 3 and piece.y == 1:
                pieces.remove(piece)
                pieces.append(Piece(piece.id, 7, 9))
            if piece.x == 3 and piece.y == 9:
                pieces.remove(piece)
                pieces.append(Piece(piece.id, 3, 1))
            if piece.x == 7 and piece.y == 1:
                pieces.remove(piece)
                pieces.append(Piece(piece.id, 3, 9))
            if piece.x == 7 and piece.y == 9:
                pieces.remove(piece)
                pieces.append(Piece(piece.id, 7, 1))

        # third poisoning post-transport
        self.poison_effect(pieces)

        ## prince joey
        # prince joey exploding
        explode = []
        joey_w, joey_b = None, None
        for piece in pieces:
            if piece.id == "J":
                joey_w = piece
            if piece.id == "j":
                joey_b = piece
        # check joey (white side)
        if joey_w is not None:
            counter = 0
            for piece in pieces:
                if piece.x == joey_w.x:
                    counter += 1
            if counter % 5 == 0:
                explode.append(joey_w)
        # check joey (black side)
        if joey_b is not None:
            counter = 0
            for piece in pieces:
                if piece.x == joey_b.x:
                    counter += 1
            if counter % 5 == 0:
                explode.append(joey_b)
        # explode joey if triggered
        for joey in explode:
            for i in range(-1, 2):
                for j in range(-1, 2):
                    for piece in pieces:
                        if piece.x == joey.x + i and piece.y == joey.y + j:
                            pieces.remove(piece)
        return pieces

    # generate new board
    def generate_board(self, pieces):
        pieces = self.after_effects(pieces)
        return Wildebeest("B", pieces, self.elapsed_time, self.total_time, self.move_count) \
               if self.player_turn == "W" else \
               Wildebeest("W", pieces, self.elapsed_time, self.total_time, self.move_count)

    # generator function yields boards for every possible move
    def possible_moves(self):
        board = self.get_board()
        pieces = self.pieces[:]
        if self.player_turn == "W":
            friendly_pieces = WHITE_ID
            enemy_pieces = BLACK_ID
        else:
            friendly_pieces = BLACK_ID
            enemy_pieces = WHITE_ID

        for piece in self.pieces:
            if piece.id in friendly_pieces:
                # gorilla
                if piece.id is "G" or piece.id is "g":
                    for move in self.legal_piece_coordinates(piece, friendly_pieces):
                        # gorilla pushes piece if not flung
                        if abs(piece.x - move[0]) > 1 or abs(piece.y - move[1]) > 1:
                            pass
                        else:
                            if board[move[0]][move[1]] is "G" or board[move[0]][move[1]] is "g":
                                continue
                            # attempts to push piece if piece found
                            if board[move[0]][move[1]] in friendly_pieces or \
                               board[move[0]][move[1]] in enemy_pieces:
                                id_pushed = board[move[0]][move[1]]
                                x_squished = (move[0] - piece.x) + move[0]
                                y_squished = (move[1] - piece.y) + move[1]
                                # cannot push piece off edge
                                if x_squished < 0 or x_squished > 10 or \
                                   y_squished < 0 or y_squished > 10:
                                    continue
                                # cannot push piece into gorilla
                                if board[x_squished][y_squished] is "G" or \
                                   board[x_squished][y_squished] is "g":
                                    continue
                                # remove pushed piece
                                pieces.remove(self.get_piece(move[0], move[1]))
                                # remove squished piece if exists
                                if board[x_squished][y_squished] in friendly_pieces or \
                                   board[x_squished][y_squished] in enemy_pieces:
                                    pieces.remove(self.get_piece(x_squished, y_squished))
                                # add pushed piece
                                pieces.append(Piece(id_pushed, x_squished, y_squished))
                        # remove old piece
                        if piece in pieces:
                            pieces.remove(piece)
                        # add new piece
                        pieces.append(Piece(piece.id, move[0], move[1]))
                        yield self.generate_board(pieces)
                        board = self.get_board() # reset temp board
                        pieces = self.pieces[:] # reset temp pieces

                # pawn becomes time machine
                elif piece.id == "P" or piece.id == "p":
                    for move in self.legal_piece_coordinates(piece, friendly_pieces):
                        # remove old piece
                        if piece in pieces:
                            pieces.remove(piece)
                        # transform pawn into time machine if reaches end of board
                        if piece.id == "P" and move[0] == 10:
                            pieces.append(Piece("H", move[0], move[1]))
                        elif piece.id == "p" and move[0] == 0:
                            pieces.append(Piece("h", move[0], move[1]))
                        # add new piece
                        else:
                            pieces.append(Piece(piece.id, move[0], move[1]))

                        # remove enemy piece
                        if board[move[0]][move[1]] in enemy_pieces:
                            pieces.remove(self.get_piece(move[0], move[1]))
                        yield self.generate_board(pieces)
                        board = self.get_board() # reset temp board
                        pieces = self.pieces[:] # reset temp pieces

                # king 
                elif piece.id == "K" or piece.id == "k":
                    for move in self.legal_piece_coordinates(piece, friendly_pieces):
                        # remove old piece
                        if piece in pieces:
                            pieces.remove(piece)
                        # transform king into king with a jet back if on middle square
                        if move[0] == 5 and move[1] == 5:
                            if piece.id == "K":
                                pieces.append(Piece("W", move[0], move[1]))
                            if piece.id == "k":
                                pieces.append(Piece("w", move[0], move[1]))
                        # add new piece
                        else:
                            pieces.append(Piece(piece.id, move[0], move[1]))
                        # remove enemy piece
                        if board[move[0]][move[1]] in enemy_pieces:
                            pieces.remove(self.get_piece(move[0], move[1]))
                        yield self.generate_board(pieces)
                        board = self.get_board() # reset temp board
                        pieces = self.pieces[:] # reset temp pieces

                # all other pieces
                else:
                    for move in self.legal_piece_coordinates(piece, friendly_pieces):
                        # remove old piece
                        if piece in pieces:
                            pieces.remove(piece)
                        # add new piece
                        pieces.append(Piece(piece.id, move[0], move[1]))
                        # remove enemy piece
                        if board[move[0]][move[1]] in enemy_pieces:
                            pieces.remove(self.get_piece(move[0], move[1]))
                        yield self.generate_board(pieces)
                        board = self.get_board() # reset temp board
                        pieces = self.pieces[:] # reset temp pieces

    # function allows user to move piece
    def move_piece(self, x, y, new_x, new_y):
        board = self.get_board()
        pieces = self.pieces[:]
        piece = self.get_piece(x, y)
        move = (new_x, new_y)

        if self.player_turn == "W":
            friendly_pieces = WHITE_ID
            enemy_pieces = BLACK_ID
        else:
            friendly_pieces = BLACK_ID
            enemy_pieces = WHITE_ID

        # check if move is legal
        if move not in self.legal_piece_coordinates(piece, friendly_pieces):
            return None

        # gorilla
        if piece.id == "G" or piece.id == "g":
            # gorilla pushes piece if not flung
            if abs(piece.x - move[0]) > 1 or abs(piece.y - move[1]) > 1:
                # remove enemy piece
                if board[move[0]][move[1]] in enemy_pieces:
                    pieces.remove(self.get_piece(move[0], move[1]))
            else:
                if board[move[0]][move[1]] == "G" or board[move[0]][move[1]] == "g":
                    return None
                # attempts to push piece if piece found
                if board[move[0]][move[1]] in friendly_pieces or \
                   board[move[0]][move[1]] in enemy_pieces:
                    id_pushed = board[move[0]][move[1]]
                    x_squished = (move[0] - piece.x) + move[0]
                    y_squished = (move[1] - piece.y) + move[1]
                    # cannot push piece off edge
                    if x_squished < 0 or x_squished > 10 or \
                       y_squished < 0 or y_squished > 10:
                        return None
                    # cannot push piece into gorilla
                    if board[x_squished][y_squished] == "G" or \
                       board[x_squished][y_squished] == "g":
                        return None
                    # remove pushed piece
                    pieces.remove(self.get_piece(move[0], move[1]))
                    # remove squished piece if exists
                    if board[x_squished][y_squished] in friendly_pieces or \
                       board[x_squished][y_squished] in enemy_pieces:
                        pieces.remove(self.get_piece(x_squished, y_squished))
                    # add pushed piece
                    pieces.append(Piece(id_pushed, x_squished, y_squished))
            # remove old piece
            if piece in pieces:
                pieces.remove(piece)
            # add new piece
            pieces.append(Piece(piece.id, move[0], move[1]))
            return self.generate_board(pieces)
            board = self.get_board() # reset temp board
            pieces = self.pieces[:] # reset temp pieces

        # pawn becomes time machine
        elif piece.id == "P" or piece.id == "p":
            # remove old piece
            if piece in pieces:
                pieces.remove(piece)
            # transform pawn into time machine if reaches end of board
            if piece.id == "P" and move[0] == 10:
                pieces.append(Piece("H", move[0], move[1]))
            elif piece.id == "p" and move[0] == 0:
                pieces.append(Piece("h", move[0], move[1]))
            # add new piece
            else:
                pieces.append(Piece(piece.id, move[0], move[1]))

            # remove enemy piece
            if board[move[0]][move[1]] in enemy_pieces:
                pieces.remove(self.get_piece(move[0], move[1]))
            return self.generate_board(pieces)
            board = self.get_board() # reset temp board
            pieces = self.pieces[:] # reset temp pieces

        # king 
        elif piece.id == "K" or piece.id == "k":
            # remove old piece
            if piece in pieces:
                pieces.remove(piece)
            # transform king into king with a jet back if on middle square
            if move[0] == 5 and move[1] == 5:
                if piece.id == "K":
                    pieces.append(Piece("W", move[0], move[1]))
                if piece.id == "k":
                    pieces.append(Piece("w", move[0], move[1]))
            # add new piece
            else:
                pieces.append(Piece(piece.id, move[0], move[1]))
            # remove enemy piece
            if board[move[0]][move[1]] in enemy_pieces:
                pieces.remove(self.get_piece(move[0], move[1]))
            return self.generate_board(pieces)
            board = self.get_board() # reset temp board
            pieces = self.pieces[:] # reset temp pieces

        # all other pieces
        else:
            # remove old piece
            if piece in pieces:
                pieces.remove(piece)
            # add new piece
            pieces.append(Piece(piece.id, move[0], move[1]))
            # remove enemy piece
            if board[move[0]][move[1]] in enemy_pieces:
                pieces.remove(self.get_piece(move[0], move[1]))
            return self.generate_board(pieces)
            board = self.get_board() # reset temp board
            pieces = self.pieces[:] # reset temp pieces

# load board from stdin
def load_board(filename=None):
    pieces = []
    i = -1
    for line in fileinput.input(filename):
        if i == 14:
            break
        if i == -1:
            player_turn = line.rstrip()
        elif i == 11:
            elapsed_time = int(line.rstrip())
        elif i == 12:
            total_time = int(line.rstrip())
        elif i == 13:
            move_count = int(line.rstrip())
        else:
            for j in range(len(line) - 1):
                if line[j] == "." or line[j] == "*" or line[j] == "#":
                    continue
                pieces.append(Piece(line[j], i, j))
        i += 1
    return Wildebeest(player_turn, pieces, elapsed_time, total_time, move_count)

# main function allows script to run to generate all boards as files
if __name__ == '__main__':
    if len(sys.argv) != 1:
        print "usage: ./wildebeest_board_generator < [board_file]"
        sys.exit(0)

    # delete previous boards
    FNULL = open(os.devnull, 'w')
    subprocess.call(["rm board.*"], shell=True, stdout=FNULL, stderr=subprocess.STDOUT)

    wildebeest = load_board()
    i = 0
    for move in wildebeest.possible_moves():
        print move
        # with open("board.{0:03d}".format(i), "w") as output:
        #     output.write("{0}".format(move))
        i += 1