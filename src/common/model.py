import torch.nn as nn

class RankerModel(nn.Module):
    def __init__(self):
        super(RankerModel, self).__init__()
        self.model = nn.Sequential(
            # First hidden layer
            nn.Linear(10, 64),
            nn.ReLU(),
            
            # Second hidden layer
            nn.Linear(64, 32),
            nn.ReLU(),
            
            # Output layer with sigmoid activation
            nn.Linear(32, 3),
            nn.Sigmoid()
        )
        
    def forward(self, x):
        return self.model(x)