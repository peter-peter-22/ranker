from src.common.transform_data import transform_data
import numpy as np
import asyncio
from src.common.fetch_data import training_data_fetcher
import torch
from src.common.model import RankerModel
from src.common.plot import display_plot
from typing import List
from src.common.model_store import save,load

async def train():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Device: {device}")
    model=RankerModel()
    model = model.to(device)
    epochs=20
    learning_rate=0.01
    criterion = torch.nn.BCELoss()
    optimizer = torch.optim.Adam(model.parameters(),lr=learning_rate)

    # Create live loss plotter
    losses: List[float]=[]

    init,get_data,close,validation_data = training_data_fetcher()
    await init()

    # Get and prepare a fixed set of training data for validation
    X_test,Y_test=transform_data(*(await validation_data()))

    for epoch in range(epochs):

        # Process the batches of data
        async for X,Y in get_data():
            # Prepare the training data for the mode
            X,Y=transform_data(X,Y)
            # Forward pass
            optimizer.zero_grad()
            outputs = model(X)
            loss:torch.Tensor = criterion(outputs, Y)
            # Backward pass and optimize
            loss.backward()
            optimizer.step()

        # Calculate and display accuracy
        with torch.no_grad():
            outputs = model(X_test)
            loss:torch.Tensor = criterion(outputs, Y_test)
            predicted = (outputs > 0.5).float()
            accuracy = (predicted == Y_test).float().mean()
            print(f'Epoch {epoch+1}, Loss: {loss.item():.4f}, Accuracy: {accuracy.item():.4f}')

        # Track the loss
        losses.append(loss.item())

    # Close the connection
    await close()

    save(model)

    # Display the plot
    display_plot(losses)

asyncio.run(train())