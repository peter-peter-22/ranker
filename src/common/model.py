import torch.nn as nn
from src.common.device import device

class RankerModel(nn.Module):
    def __init__(self):
        super(RankerModel, self).__init__()
        self.model = nn.Sequential(
            # First hidden layer
            nn.Linear(10, 16),
            nn.ReLU(),
            
            # Second hidden layer
            nn.Linear(16, 16),
            nn.ReLU(),
            
            # Output layer with sigmoid activation
            nn.Linear(16, 3),
            nn.Sigmoid()
        )
        
    def forward(self, x):
        return self.model(x)
    
def create_model():
    """Create an empty model"""
    model=RankerModel()
    model=model.to(device)
    return model