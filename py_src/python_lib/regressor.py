import torch
from torch import nn

class MLPRegressor(nn.Module):
    def __init__(self, inp_size, hidden_sizes = [128], out_size=1, device=None):
        """
        Arguments
        inp_size
        hidden_sizes: size of hidden layers
        out_size
        """
        super().__init__()
        
        # if no device provided, detect device, else use cpu
        self.device = ('cuda' if torch.cuda.is_available() else 'cpu') if device == None else 'cpu'
        print(f'using {self.device}')

        ll = lambda in_size, out_size: nn.Linear(in_size, out_size).cuda() if self.device == 'cuda' else nn.Linear(in_size, out_size)

        self.layer_in = ll(inp_size, hidden_sizes[0])
        self.hidden_layers = []
        for i in range(len(hidden_sizes) - 1):
            self.hidden_layers.append(ll(hidden_sizes[i], hidden_sizes[i+1]))
        self.layer_out = ll(hidden_sizes[-1], out_size)

    def forward(self, x):
        x = self.layer_in(x)
        for layer in self.hidden_layers:
            x = nn.functional.relu(x)
            x = layer(x)
        x = nn.functional.relu(x)
        x = self.layer_out(x)
        return x
    
def train_net(net, optimizer, loss_function, X, y, training_epochs = 2000):
    """
    Arguments
    net
    optimizer
    loss_function
    inputs
    labels
    """
    for i in range(training_epochs):
        optimizer.zero_grad()
        outputs = net(X)
        loss = loss_function(outputs, y)
        # print(loss.item())
        loss.backward()
        optimizer.step()

        if i % 100 == 99:
            print(f'step {i} loss: {loss.item()}')
    
    return loss_function(net(X), y).item()

# TODO: bag regressors