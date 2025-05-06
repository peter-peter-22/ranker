from typing import NamedTuple, List
import numpy as np
from src.common.fetch_data import PostToRank,Engagements
import torch

class PostToRankNormalized(NamedTuple):
    """Normalized post data for the model."""
    age: float    
    like_count_normalized: float
    reply_count_normalized: float
    click_count_normalized: float
    embedding_similarity: float
    like_history_normalized: float
    reply_history_normalized: float
    click_history_normalized: float
    followed: float
    replied_by_followed: float

def transform_post(post:PostToRank):
    """
    Prepare a post to be used in the model by normalizing the values.

    Args:
        post (PostToRank): The post to transform.

    Returns:
        PostToRankNormalized: A post with normalized values for the model.
    """
    return PostToRankNormalized(
        # Convert to hours and normalize.
        age=post.age.seconds/60/48,
        # Embedding similarity.
        embedding_similarity=post.embedding_similarity,
        # Normalize engagement counts.
        like_count_normalized=np.log10(max(post.like_count,1))/5,
        reply_count_normalized=np.log10(max(post.reply_count,1))/5,
        click_count_normalized=np.log10(max(post.click_count,1))/5,
        # Normalize engagement history counts.
        like_history_normalized=np.log10(max(post.like_history,1)),
        reply_history_normalized=np.log10(max(post.reply_history,1)),
        click_history_normalized=np.log10(max(post.click_history,1)),
        # Convert bools to float.
        followed=post.followed,
        replied_by_followed=post.replied_by_followed,
    )

def transform_data(posts:List[PostToRank],engagements:List[Engagements]):
    """
    Convert the training data to normalized tensors

    Args:
        posts (List[PostToRank]): The training data.
        engagements (List[Engagements]): The engagement history.

    Returns:
        Tuple[torch.Tensor, torch.Tensor]: The normalized tensors.
    """
    posts:torch.Tensor=torch.stack([torch.tensor(transform_post(row),dtype=torch.float32) for row in posts])#TODO use float16
    engagements:torch.Tensor=torch.stack([torch.tensor(row,dtype=torch.float32) for row in engagements])
    return posts,engagements
