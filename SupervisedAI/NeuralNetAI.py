from supervised_engine import board_to_tensor, get_valid_moves, move_to_code, get_codes_dict
from supervised_engine import *
import numpy as np
import torch
def get_best_move(board_stack, NN):
    columns = {k: v for v, k in enumerate("abcdefgh")}
    codes = get_codes_dict()
    board_tensor = board_to_tensor(board_stack)
    board_tensor = to_gpu(board_tensor)
    #probability, value = NN(board_tensor, 1, do_softmax=True)
    probability = NN(board_tensor, 1, do_softmax=True)
    probability = torch.reshape(probability, (8, 8, 76))
    valid_moves = get_valid_moves(board_stack[7])
    probabilities = []
    moves = []
    for move in valid_moves:
        probabilities.append(probability[columns[move[0]], int(move[1])-1, codes[move_to_code(board_stack[7], move, board_stack[7].turn)]].item())
        moves.append(move)
    move_index = probabilities.index(max(probabilities))
    move = moves[move_index]
    print(move)
    return move