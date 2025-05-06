import torch
from pathlib import Path
from src.app import root_path

model_path=(root_path / Path("model/model.pth")).resolve()

def save(model):
    torch.save(model, model_path)
    print(f"Saved model to {model_path}")

def load():
    print(f"Loading model from {model_path}")
    return torch.load(model_path)