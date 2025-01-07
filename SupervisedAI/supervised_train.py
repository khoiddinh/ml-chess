import chess.pgn
from supervised_engine import *
import numpy as np
import torch
from torch import nn
import random
#from Resnet_Model import Network
from simplified_model import Network
import pickle
import pandas as pd
#pgn = open(r'C:\Users\hi2kh\OneDrive\Desktop\Machine Learning Pytorch\Chess\database.pgn')
pgn = open(r'C:\Users\hi2kh\OneDrive\Desktop\Machine Learning Pytorch\SupervisedAI\Stockfish_14.pgn')
codes = get_codes_dict()
columns = {k: v for v, k in enumerate("abcdefgh")}

def get_winner(game):
    result = str(game.headers["Result"])
    if "/" in result:
        return 0
    elif result == "1-0":
        return 1
    else:
        return -1
def get_dataset():
    length = 0
    stop = False
    for i in range(2040):
    #for i in range(1):
        print(i)
        board_states = []
        move_states = []
        game = chess.pgn.read_game(pgn)
        board = game.board()
        board_stack = [board for _ in range(8)]
        for move in game.mainline_moves():
            move = str(board.parse_san(str(move)))
            bitboards = board_to_tensor(board_stack)
            move_tensor = np.zeros((8, 8, 76))
            move_tensor[columns[move[0]], int(move[1])-1, codes[move_to_code(board, move, board.turn)]] = 1
            move_tensor = np.reshape(move_tensor, (4864,))
            board_states.append(bitboards)
            move_states.append(np.argmax(move_tensor))
            move = chess.Move.from_uci(move)
            board.push(move)
            del board_stack[0]
            board_stack.append(board)
            length += 1
            if length == dataset_size:
                stop = True
                break
        winner = get_winner(game)
        for x in range(len(board_states)):
            board_tensors.append(board_states[x].numpy())
            move_tensors.append(move_states[x])
            winner_tensors.append(winner)
        if stop:
                break

#with open('data.pkl', 'wb') as f:
    #pickle.dump(board_tensors, f)
    #pickle.dump(move_tensors, f)
    #pickle.dump(winner_tensors, f)

#with open('data.pkl', 'rb') as f:
 #   _board = pickle.load(f)
  #  _move = pickle.load(f)
   # _winner = pickle.load(f)
def train_batch(x_input, policy_expected, value_expected, batch_size):
    losses = []
    for iteration in range(1000):  # Stop condition for gradient descent
        optimizer.zero_grad()
        # Forward Propagation
        #policy_output, value_output = NN(x_input, batch_size=batch_size)
        policy_output = NN(x_input, batch_size=batch_size)
        #print(policy_output.size())
        #print(policy_expected.size())
        #policy_output = torch.reshape(policy_output, (1000, 4864))
        #policy_output = torch.reshape(policy_output, (batch_size, 4864))
        # Calculate Loss Function
        policy_expected = torch.add(policy_expected, 0.000001)
        cross_entropy = nn.CrossEntropyLoss()
        mean_square = nn.MSELoss()
        loss = cross_entropy(policy_output, policy_expected.long()) #+ mean_square(value_output, value_expected)
        #loss = mean_square(policy_output, policy_expected) #+ mean_square(value_output, value_expected)
        print(loss)
        losses.append(loss)
        # Step Gradient

        loss.backward()
        nn.utils.clip_grad_norm_(NN.parameters(), 1)
        optimizer.step()
    if True in losses:
        print("NAN")

def shuffle_seed():
    return 0.5
torch.autograd.set_detect_anomaly(True)
board_tensors = []
move_tensors = []
winner_tensors = []
#dataset is 269000
dataset_size = 5000
batch_size = 500
get_dataset()
NN = Network()
NN.to('cuda')
random.shuffle(board_tensors, shuffle_seed)
random.shuffle(move_tensors, shuffle_seed)
random.shuffle(winner_tensors, shuffle_seed)
optimizer = torch.optim.Adam(NN.parameters(), lr=0.00001)
board_tensors = np.array(board_tensors)
move_tensors = np.array(move_tensors)
winner_tensors = np.array(winner_tensors)
board_tensors = torch.cuda.FloatTensor(board_tensors)
move_tensors = torch.cuda.FloatTensor(move_tensors)
winner_tensors = torch.cuda.FloatTensor(winner_tensors)
board_tensors = torch.reshape(board_tensors, (dataset_size//batch_size, batch_size, 97, 8, 8))
move_tensors = torch.reshape(move_tensors, (dataset_size//batch_size, batch_size))
winner_tensors = torch.reshape(winner_tensors, (dataset_size//batch_size, batch_size))



for epoch in range(1):
    print(f"Epoch: {epoch}")
    for i in range(2):
        print(i)
        x_input = board_tensors[i]
        policy_expected = move_tensors[i]
        value_expected = winner_tensors[i]
        x_input.to('cuda')
        policy_expected.to('cuda')
        value_expected.to('cuda')
        train_batch(x_input, policy_expected, value_expected, batch_size=batch_size)
        FILE = "chess_stockfish2.pth"
        torch.save(NN, FILE)


