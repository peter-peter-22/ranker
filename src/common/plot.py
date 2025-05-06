import matplotlib.pyplot as plt
from typing import List

def display_plot(losses: List[float]):
    """
    Display array of losses in a plot.
    """
    plt.figure(figsize=(8, 5))
    plt.plot(losses, label='Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    plt.title('Training Loss')
    plt.show()
