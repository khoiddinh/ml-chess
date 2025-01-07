import chess
import numpy as np
import torch

fen_data = {
    'P': 1,
    'N': 2,
    'B': 3,
    'R': 4,
    'Q': 5,
    'K': 6,
    'p': -1,
    'n': -2,
    'b': -3,
    'r': -4,
    'q': -5,
    'k': -6
}

piece_dict = {
    1: "pawn",
    2: "knight",
    3: "bishop",
    4: "rook",
    5: "queen",
    6: "king"
}

promotion_dict = {
    "n": "knight",
    "b": "bishop",
    "r": "rook",
    "q": "queen"
}
def get_valid_moves(board_state):
    # returns numpy array of possible moves
    # as uci strings
    possible_moves = list(board_state.legal_moves)
    possible_moves = np.array(possible_moves)
    for i in range(possible_moves.size):
        move = possible_moves[i]
        uci_move = chess.Move.uci(move)
        possible_moves[i] = uci_move
    return possible_moves

def board_to_tensor(board_states):
    # takes np array of 8 board states in format chess.Board() objects
    # returns stack of bitmasks for each state
    def _get_bitmask(board):
        bit_board = []
        fen = board.fen()
        board_list = parse_fen(fen)
        # white_pieces
        for i in range(6):
            this_bitboard = np.where(board_list != i, 0, board_list)
            this_bitboard = np.where(this_bitboard == i, 1, this_bitboard)
            bit_board.append(this_bitboard.tolist())
        # black_pieces
        for i in range(6):
            i = -i
            this_bitboard = np.where(board_list != i, 0, board_list)
            this_bitboard = np.where(this_bitboard == i, 1, this_bitboard)
            bit_board.append(this_bitboard.tolist())
        return bit_board
    board_state_bitmasks = list(map(_get_bitmask, board_states))
    board_state_bitmasks = np.array(board_state_bitmasks)
    board_state_bitmasks = np.reshape(board_state_bitmasks, (96, 8, 8))
    board_state_bitmasks = board_state_bitmasks.tolist()
    if board_states[7].turn:
        board_state_bitmasks.append(np.zeros((8, 8)).tolist())
        #board_state_bitmasks = np.append(board_state_bitmasks, np.zeros((8, 8)))
    else:
        board_state_bitmasks.append(np.ones((8, 8)).tolist())
        #board_state_bitmasks = np.append(board_state_bitmasks, np.ones((8, 8)))
    bitmask_tensor = torch.tensor(board_state_bitmasks)
    bitmask_tensor = torch.reshape(bitmask_tensor, (1, 97, 8, 8))
    return bitmask_tensor

def to_gpu(tensor):
    print(tensor)
    new_tensor = tensor.to(device='cuda')
    return new_tensor
def parse_fen(fen):
    fen_list_raw = fen.split('/')
    last_term = fen_list_raw[7]
    last_term = last_term.split(' ')
    last_term = last_term[0]
    fen_list = fen_list_raw[:7]
    fen_list.append(last_term)
    board = []
    for rows in fen_list:
        row = []
        for character in rows:
            try:
                for x in range(int(character)):
                    row.append(0)
            except:
                piece = fen_data.get(character)
                row.append(piece)
        board.append(row)
    board = np.array(board)
    return board

def get_codes_dict():
    codes, i = {}, 0
    for nSquares in range(1,8):
        for direction in ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]:
            codes[(nSquares, direction)] = i
            i += 1
    for two in ["N","S"]:
        for one in ["E","W"]:
            codes[("knight", two, one)] , i = i , i + 1
    for two in ["E","W"]:
        for one in ["N","S"]:
            codes[("knight", two, one)] , i = i , i  + 1
    for move in ["N","NW","NE"]:
        for promote_to in ["rook", "knight", "bishop", "queen"]:
            codes[("promotion", move, promote_to)] , i = i , i + 1
    return codes

def move_to_code(board_state, move, player_turn):
    # accepts board_state as chess.Board() object
    # board_state is the board before the move
    # code_dict = pre compiled dict with codes
    # move is string in uci format len 5 for promotion or len 4 for normal
    # player_turn = bool, white = True, black = False
    # returns tuple to access moves in code_dict
    columns = {k: v for v, k in enumerate("abcdefgh")}
    fen = board_state.fen()
    board_array = parse_fen(fen)

    x = 8 - int(move[1])
    y = columns[move[0]]
    piece_number = abs(board_array[x][y])
    if player_turn:
        if len(move) == 5:
            direction = "N"
            if columns[move[0]] > columns[move[2]]:
                direction += "W"
            elif columns[move[0]] == columns[move[2]]:
                pass
            else:
                direction += "E"
            code = ("promotion", direction, promotion_dict[move[4]])

        else:
            if piece_number == 2:
                if columns[move[0]] > columns[move[2]]:
                    horizontal_direction = "W"
                else:
                    horizontal_direction = "E"
                if int(move[1]) > int(move[3]):
                    vertical_direction = "S"
                else:
                    vertical_direction = "N"
                code = ("knight", vertical_direction, horizontal_direction)
            else:
                direction = ""
                if int(move[1]) > int(move[3]):
                    direction += "S"
                elif int(move[1]) == int(move[3]):
                    pass
                else:
                    direction += "N"
                if columns[move[0]] > columns[move[2]]:
                    direction += "W"
                elif columns[move[0]] == columns[move[2]]:
                    pass
                else:
                    direction += "E"
                if abs(int(move[1])-int(move[3])) != 0:
                    code = (abs(int(move[1])-int(move[3])), direction)
                else:
                    code = (abs(columns[move[0]]-columns[move[2]]), direction)

    else:
        if piece_number == 2:
            if columns[move[0]] < columns[move[2]]:
                horizontal_direction = "W"
            else:
                horizontal_direction = "E"
            if int(move[1]) < int(move[3]):
                vertical_direction = "S"
            else:
                vertical_direction = "N"
            code = ("knight", vertical_direction, horizontal_direction)
        else:
            direction = ""
            if int(move[1]) < int(move[3]):
                direction += "S"
            elif int(move[1]) == int(move[3]):
                pass
            else:
                direction += "N"
            if columns[move[0]] < columns[move[2]]:
                direction += "W"
            elif columns[move[0]] == columns[move[2]]:
                pass
            else:
                direction += "E"
            if abs(int(move[1]) - int(move[3])) != 0:
                code = (abs(int(move[1]) - int(move[3])), direction)
            else:
                code = (abs(columns[move[0]] - columns[move[2]]), direction)
    code = list(code)
    code = [x for x in code if x is not None]
    code = tuple(code)
    return code


def normalize_data(input_list):
    # returns map
    def _norm(element):
        return (element-minimum)/(maximum-minimum)
    minimum = min(input_list)
    maximum = max(input_list)
    normalized_list = list(map(_norm, input_list))
    return normalized_list


def get_winner(game_state):
    # return 1 if white wins, return -1 if black wins, return 0 if draw
    winner = chess.Board.outcome(game_state)
    print(winner)
    if winner.winner is None:
        return 0
    elif winner.winner:
        return 1
    else:
        return -1


def game_end(game_state):
    if game_state.is_checkmate() or game_state.is_stalemate() or game_state.is_insufficient_material():
        return True
    else:
        return False


#board_state = chess.Board('8/8/8/8/8/2k5/1q6/K7')
#board_state.turn = True
#print(get_winner(board_state))
#print(board_state)
