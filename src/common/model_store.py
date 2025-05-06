import torch
from pathlib import Path
from src.app import root_path
from src.common.model import RankerModel

model_path=(root_path / Path("model/model.pth")).resolve()

cached_model:RankerModel = None

def save(model:RankerModel):
    torch.save(model.state_dict(), model_path)
    print(f"Saved model to {model_path}")

def load()->RankerModel:
    global cached_model
    if cached_model:
       print("Loaded model from cache")
       return cached_model
    
    print(f"Loading model from {model_path}")
    cached_model=RankerModel()
    cached_model.load_state_dict(torch.load(model_path))
    return cached_model