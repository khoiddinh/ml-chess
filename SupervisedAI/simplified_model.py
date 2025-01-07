import torch
from torch import nn

class Network(nn.Module):
    def __init__(self):
        super().__init__()
        self.layers = nn.ModuleList()
        self.layers.append(nn.Conv2d(97, 128, (3, 3), padding="same"))
        self.layers.append(nn.MaxPool2d(2, 2))
        self.layers.append(nn.BatchNorm2d(num_features=128))
        self.layers.append(nn.Sigmoid())
        self.layers.append(nn.Conv2d(128, 128, (3, 3), padding="same"))
        self.layers.append(nn.MaxPool2d(2, 2))
        self.layers.append(nn.BatchNorm2d(num_features=128))
        self.layers.append(nn.Sigmoid())
        self.layers.append(nn.Flatten())
        self.policy_head = PolicyHead()
        #self.value_head = ValueHead()

    def forward(self, x_input, batch_size, do_softmax=False):
        this_layer = x_input
        for layer in self.layers:
            this_layer = layer(this_layer)
            if not torch.isfinite(this_layer).all():
                print(this_layer)
        policy_head = self.policy_head(this_layer, batch_size=batch_size, do_softmax=do_softmax)
        #value_head = self.value_head(this_layer)
        return policy_head#, value_head


class PolicyHead(nn.Module):
    def __init__(self):
        super().__init__()
        self.layers = nn.ModuleList()
        self.layers.append(nn.Linear(512, 1024))
        self.layers.append(nn.Sigmoid())
        self.layers.append(nn.Linear(1024, 2432))
        self.layers.append(nn.Sigmoid())
        self.layers.append(nn.Linear(2432, 4864))
        self.layers.append(nn.Sigmoid())
        #self.layers.append(nn.BatchNorm1d(num_features=4864))

    def forward(self, x_input, batch_size, do_softmax=False):
        this_layer = x_input
        count = 0
        for layer in self.layers:
            this_layer = layer(this_layer)
            count += 1
            if not torch.isfinite(this_layer).all():
                print("E")
                print(count)
                print(this_layer)
        if do_softmax:
            softmax = nn.Softmax(dim=1)
            this_layer = softmax(this_layer)
        #this_layer = torch.reshape(this_layer, (batch_size, 8, 8, 76))
        return this_layer

class ValueHead(nn.Module):
    def __init__(self):
        super().__init__()
        self.layers = nn.ModuleList()
        self.layers.append(nn.Linear(512, 128))
        self.layers.append(nn.BatchNorm1d(num_features=128))
        self.layers.append(nn.Sigmoid())
        self.layers.append(nn.Linear(128, 1))
        self.layers.append(nn.Tanh())

    def forward(self, x_input):
        this_layer = x_input
        for layer in self.layers:
            this_layer = layer(this_layer)
        return this_layer

