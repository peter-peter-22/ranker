import matplotlib.pyplot as plt
from typing import List, NamedTuple

class TrainingProgress(NamedTuple):
    loss: float
    accuracy: float

def display_plot(progress: List[TrainingProgress]):
    """
    Display array of losses in a plot.
    """
    plt.figure(figsize=(8, 5))
    plt.plot([t.loss for t in progress], label='Loss')
    plt.plot([t.accuracy for t in progress], label='Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Value')
    plt.ylim(0, 1)
    plt.legend()
    plt.grid(True)
    plt.title('Training Loss and Accuracy')
    plt.show()
