import numpy as np
from sklearn.model_selection import train_test_split
from collections import defaultdict
from sklearn.preprocessing import normalize
from tabulate import tabulate
import torch
import torch.nn as nn
from torch.nn import functional as F
import torch.optim as optim
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from torch.utils.data import TensorDataset, DataLoader
import asyncio

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')