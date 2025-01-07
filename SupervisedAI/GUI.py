from GUI_engine import *
#from simplified_model import Network
from NeuralNetAI import get_best_move
import torch
import copy
import pygame
import chess

FILE = "chess_stockfish.pth"
NN = torch.load(FILE)
NN.eval()
board_stack = [chess.Board() for _ in range(8)]
gameboard = board_stack[7]
pygame.init()
height, width = 720, 720
WIN = pygame.display.set_mode((height, width))
FPS = 60
timer = pygame.time.Clock()
pygame.display.set_caption("Chess")
run = True
color_to_move = 0
ai_color = 1
white_win = False
black_win = False
draw = False
selected_piece = False
possible_move_spaces = []
gameboard_list = None
just_switched = False
load_textures()
fen = gameboard.fen()
gameboard_list = parse_fen(fen)
while run:
    timer.tick(FPS)
    if just_switched:
        board_stack.append(gameboard)
        del board_stack[0]
        possible_move_spaces.clear()
        fen = gameboard.fen()
        gameboard_list = parse_fen(fen)
        if check_winner(gameboard) == 1:
            white_win = True
            run = False
            continue
        elif check_winner(gameboard) == 2:
            black_win = True
            run = False
            continue
        elif check_winner(gameboard) == 3:
            draw = True
            run = False
            continue

        elif color_to_move == ai_color:
            pygame.event.get()
            draw_board(gameboard_list, possible_move_spaces, WIN)
            ai_move = get_best_move(board_stack, NN)
            ai_move = chess.Move.from_uci(ai_move)
            print(ai_move)
            gameboard.push(ai_move)
            color_to_move = switch_player_turn(color_to_move)
            continue
        elif check_winner(gameboard) == 0:
            just_switched = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_presses = pygame.mouse.get_pressed()
            if mouse_presses[0]:
                pos = pygame.mouse.get_pos()
                coordinates = find_square_clicked(pos)
                if selected_piece:
                    if previous_piece_coordinates == coordinates:
                        selected_piece = False
                        possible_move_spaces.clear()
                        continue
                    if color_to_move == 0 and gameboard_list[coordinates[0]][coordinates[1]] > 0:
                        possible_move_spaces.clear()
                        previous_piece_coordinates = coordinates
                        possible_move_spaces = copy.deepcopy(find_valid_moves_for_piece(gameboard, previous_piece_coordinates))
                        continue
                    elif color_to_move == 1 and gameboard_list[coordinates[0]][coordinates[1]] < 0:
                        possible_move_spaces.clear()
                        previous_piece_coordinates = coordinates
                        possible_move_spaces = copy.deepcopy(find_valid_moves_for_piece(gameboard, previous_piece_coordinates))
                        continue
                    if is_valid_move(gameboard, coord_to_move(gameboard_list, previous_piece_coordinates, coordinates)):
                        gameboard = copy.deepcopy(move_piece(gameboard, coord_to_move(gameboard_list, previous_piece_coordinates, coordinates)))
                        print("MOVED")
                        selected_piece = False
                        just_switched = True
                        color_to_move = copy.deepcopy(switch_player_turn(color_to_move))
                        previous_piece_coordinates = []
                        continue
                    else:
                        selected_piece = False
                        previous_piece_coordinates = []
                        possible_move_spaces.clear()
                else:
                    if gameboard_list[coordinates[0]][coordinates[1]] == 0:
                        continue
                    else:
                        previous_piece_coordinates = coordinates
                        if color_to_move == 0 and gameboard_list[previous_piece_coordinates[0]][previous_piece_coordinates[1]] > 0:
                            possible_move_spaces = copy.deepcopy(find_valid_moves_for_piece(gameboard, previous_piece_coordinates))
                            selected_piece = True
                        elif color_to_move == 1 and gameboard_list[previous_piece_coordinates[0]][previous_piece_coordinates[1]] < 0:
                            possible_move_spaces = copy.deepcopy(find_valid_moves_for_piece(gameboard, previous_piece_coordinates))
                            selected_piece = True
                        else:
                            continue
    draw_board(gameboard_list, possible_move_spaces, WIN)
pygame.quit()
if white_win:
    print("WHITE WON!")
elif black_win:
    print("BLACK WON!")
elif draw:
    print("DRAW!")
else:
    print("USER STOPPED!")
