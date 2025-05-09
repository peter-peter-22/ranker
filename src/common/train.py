from src.common.transform_data import transform_posts,transform_engagements
import asyncio
from src.common.fetch_data import training_data_fetcher
from src.common.model import create_model
from src.common.plot import display_plot
from typing import List
from src.common.model_store import save
from src.common.plot import TrainingProgress
import torch
from src.model.early_stoppping import EarlyStopping

async def train():

    # Create model and define config
    model=create_model()
    epochs=5
    learning_rate=0.02
    criterion = torch.nn.BCELoss()
    optimizer = torch.optim.Adam(model.parameters(),lr=learning_rate)
    early_stopper = EarlyStopping(patience=3, min_delta=0.001)

    # Track loss and accuracy
    training_progress: List[TrainingProgress]=[]

    # Create training data streamer
    init,get_data,close,validation_data = training_data_fetcher()
    await init()

    # Get a fixed set of training data for validation
    X_test,Y_test=await validation_data()
    # Prepare training data for the model
    X_test=transform_posts(X_test)
    Y_test=transform_engagements(Y_test)

    for epoch in range(epochs):

        # Train
        async for X,Y in get_data():
            print("Training")
            # Prepare the training data for the model
            X=transform_posts(X)
            Y=transform_engagements(Y)
            # Forward pass
            optimizer.zero_grad()
            outputs:torch.Tensor = model(X)
            loss:torch.Tensor = criterion(outputs, Y)
            # Backward pass and optimize
            loss.backward()
            optimizer.step()
            print("Training complete")

        # Evaluate
        with torch.no_grad():
            outputs:torch.Tensor = model(X_test)
            loss:torch.Tensor = criterion(outputs, Y_test)
        predicted = (outputs > 0.5).float()
        accuracy = (predicted == Y_test).float().mean()
        print(f'Epoch {epoch+1}, Loss: {loss.item():.4f}, Accuracy: {accuracy.item():.4f}')
        # Update training metrics
        training_progress.append(TrainingProgress(loss.item(), accuracy.item()))

        # Early stopping
        if early_stopper.step(accuracy):
            print("Early stopping triggered.")
            break

    # Close the connection
    await close()

    # Save after the training is complete
    save(model)

    # Display the plot
    display_plot(training_progress)

asyncio.run(train())