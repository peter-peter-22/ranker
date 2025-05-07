import torch

force_cpu=True
device = torch.device('cuda' if torch.cuda.is_available() and not force_cpu else 'cpu')
print(f"Device: {device}")