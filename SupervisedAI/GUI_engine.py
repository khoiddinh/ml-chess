import chess
import pygame
import random
import copy

def find_valid_moves(local_board):
    return local_board.legal_moves

pieces = {
    1: "W Pawn",
    2: "W Knight",
    3: "W Bishop",
    4: "W Rook",
    5: "W Queen",
    6: "W King",
    -1: "B Pawn",
    -2: "B Knight",
    -3: "B Bishop",
    -4: "B Rook",
    -5: "B Queen",
    -6: "B King"
}
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
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (100, 70, 36)
GRAY = (105, 113, 125)
global piece_textures
piece_textures = {}


def create_board():  # near player color => 0 = white, 1 = black
    board = []
    for x in range(8):
        if x == 0 or x == 7:
            starting_row = [4, 2, 3, 5, 6, 3, 2, 4]
            board.append(starting_row)
        elif x == 1 or x == 6:
            starting_row = [1 for ones in range(8)]
            board.append(starting_row)
        else:
            starting_row = [0 for zeros in range(8)]
            board.append(starting_row)
    for x in range(2):
        for y in range(8):
            board[x][y] = board[x][y] * -1
    return board


def load_textures():
    global piece_textures
    for x in range(-6, 7):
        if x == 0:
            continue
        else:
            piece_textures[x] = pygame.image.load(f'Assets/{pieces.get(x)}.png')
def color_to_color(bool):
    if bool:
        return 0
    else:
        return 1

def do_random_move(board):
    move_list = list(board.legal_moves)
    move = random.randint(0, len(move_list)-1)
    board.push(move_list[move])
    return board

def find_valid_moves_for_piece(board, piece_coord):
    fen = board.fen()
    game_list = parse_fen(fen)
    valid_moves = list(board.legal_moves)
    if game_list[piece_coord[0]][piece_coord[1]] == 1:
        print(f"Valid Moves: {valid_moves}")
    letter_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    uci_format_coord = str(letter_list[piece_coord[1]]) + str((8-piece_coord[0]))
    moves = []
    valid_moves_new = []
    for move in valid_moves:
        valid_moves_new.append(str(move))
    print(valid_moves_new)
    for letters in letter_list:
        for x in range(1, 9):
            if uci_format_coord+letters+str(x) in valid_moves_new:
                moves.append([8-x, letter_list.index(letters)])
            elif uci_format_coord+letters+str(x) + "q" in valid_moves_new:
                moves.append([8-x, letter_list.index(letters)])
    print(moves)

    return moves

def coord_to_move(game_list, original_coord, new_coord = None):
    letter_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    uci_format_coord = str(letter_list[original_coord[1]]) + str((8 - original_coord[0]))
    uci_format_coord_new = str(letter_list[new_coord[1]]) + str((8 - new_coord[0]))
    if abs(game_list[original_coord[0]][original_coord[1]]) == 1 and (new_coord[0] == 0 or new_coord[0] == 7):
        uci_format_coord_new += "q"
    if new_coord is not None:
        return uci_format_coord+uci_format_coord_new
    else:
        return uci_format_coord

def check_winner(board): #0 = no winner, 1 = white, 2 = black, 3 = draw
    turn = board.turn
    if turn: #white turn
        if board.is_checkmate():
            return 2
        elif board.is_stalemate() or board.is_insufficient_material():
            return 3
        else:
            return 0
    else:
        if board.is_checkmate():
            return 1
        elif board.is_stalemate() or board.is_insufficient_material():
            return 3
        else:
            return 0
def switch_player_turn(turn):
    if turn == 0:
        return 1
    else:
        return 0



def find_square_clicked(coord_of_mouse):  # returns [x, y] board list coordinates
    x, y = coord_of_mouse
    x_count = 0
    y_count = 0
    while x > 90:
        x = x - 90
        x_count += 1
    while y > 90:
        y = y - 90
        y_count += 1
    return [y_count, x_count]

def is_valid_move(board, move_local):
    move = copy.deepcopy(move_local)
    valid_moves_raw = list(board.legal_moves)
    valid_moves = []
    for moves in valid_moves_raw:
        valid_moves.append(str(moves))
    print(valid_moves)
    print(move)
    if move in valid_moves:
        return True
    elif move + "q" in valid_moves:
        return True
    else:
        return False

def move_piece(board, move):
    move = chess.Move.from_uci(move)
    board.push(move)
    return board
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
    return board
def draw_board(board, spaces_attacked, game_window):  # near player color 0 = white, 1 = black
    # if near player color == black => must pass in mirrored gameboard
    game_window.fill(WHITE)
    starting_color = 0  # white = 0, black = 1
    for x in range(8):
        current_color = starting_color
        for y in range(8):
            if current_color == 0:
                if [x, y] in spaces_attacked:
                    pygame.draw.rect(game_window, GRAY, (y * 90, x * 90, 90, 90))
                current_color = 1
            else:
                current_color = 0
                if [x, y] in spaces_attacked:
                    pygame.draw.rect(game_window, GRAY, (y * 90, x * 90, 90, 90))
                else:
                    pygame.draw.rect(game_window, BROWN, (y * 90, x * 90, 90, 90))
        if starting_color == 0:
            starting_color = 1
        else:
            starting_color = 0
    for x in range(8):
        for y in range(8):
            if board[x][y] != 0:
                try:
                    texture = piece_textures[board[x][y]]
                except:
                    pass
                game_window.blit(texture, (y * 90, x * 90))
    pygame.display.flip()


