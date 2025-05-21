import torch
from typing import List,NamedTuple
from src.common.fetch_data import PostToRank
from src.common.model_store import load
from src.common.transform_data import transform_posts

class PredictedEngagements(NamedTuple):
    like_chance:float
    reply_chance:float
    click_chance:float

def predict(posts:List[PostToRank]):
    # Get the model
    model=load()
    # Prepare posts for the model
    prepared_posts=transform_posts(posts)
    # Make predictions
    with torch.no_grad():
        predictions:torch.Tensor=model(prepared_posts)
    # Convert to readable format
    return [PredictedEngagements(*row) for row in predictions.tolist()] # type: ignore
