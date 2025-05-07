from typing import NamedTuple, List
import numpy as np
from src.common.fetch_data import PostToRank,Engagements
import torch
from src.common.device import device

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

def normalize_post(post:PostToRank):
    """
    Prepare a post to be used in the model by normalizing the values.

    Args:
        post (PostToRank): The post to transform.

    Returns:
        PostToRankNormalized: A post with normalized values for the model.
    """
    return PostToRankNormalized(
        # Convert to hours and normalize.
        age=post.age.seconds/60/60/48,
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

def transform_posts(posts:List[PostToRank]):
    """
    Normalize posts and convert them to tensors.

    Args:
        posts (List[PostToRank]): Posts to transform.

    Returns:
        torch.Tensor: Normalized post tensors.
    """
    posts:torch.Tensor=torch.stack([torch.tensor(normalize_post(row),device=device,dtype=torch.float32) for row in posts])#TODO use float16
    return posts

def transform_engagements(engagements:List[Engagements]):
    """
    Convert engagements to tensors.

    Args:
        engagements (List[Engagements]): The engagements to convert.

    Returns:
        torch.Tensor: The engagement tensors.
    """
    engagements:torch.Tensor=torch.stack([torch.tensor(row,device=device,dtype=torch.float32) for row in engagements])
    return engagements
