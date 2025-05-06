from src.common.transform_post import transform_post
import numpy as np
import asyncio
from src.common.fetch_data import create_data_stream
import torch
from src.common.model import RankerModel

async def train():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Device: {device}")
    model=RankerModel()
    #model = model.to(device)
    epochs=10
    batch_size = 512
    learning_rate=0.01
    criterion = torch.nn.BCELoss()
    optimizer = torch.optim.Adam(model.parameters(),lr=learning_rate)


    init,get_data,close = create_data_stream()
    await init()
    for epoch in range(epochs):
        async for X,Y in get_data():
                X=torch.stack([torch.tensor(transform_post(row),dtype=torch.float32) for row in X])
                Y=torch.stack([torch.tensor(row,dtype=torch.float32) for row in Y])

                # Forward pass
                optimizer.zero_grad()
                outputs = model(X)
                loss:torch.Tensor = criterion(outputs, Y)

                # Backward pass and optimize
                loss.backward()
                optimizer.step()

                with torch.no_grad():
                    outputs = model(X)
                    predicted = (outputs > 0.5).float()
                    accuracy = (predicted == Y).float().mean()
                    print(f'Epoch {epoch+1}, Loss: {loss.item():.4f}, Accuracy: {accuracy.item():.4f}')
    await close()

asyncio.run(train())