from typing import NamedTuple
import numpy as np

class ModelInput(NamedTuple):
    like_count_normalized: float
    reply_count_normalized: float
    click_count_normalized: float
    age: float    
    like_history_normalized: float
    reply_history_normalized: float
    click_history_normalized: float
    embedding_similarity: float
    followed: float
    replied_by_followed: float
    follower_count_normalized: float

class PostToRank(NamedTuple):
    like_count: int
    reply_count: int
    click_count: int
    age: float    
    like_history: int
    reply_history: int
    click_history: int
    embedding_similarity: float
    followed: bool
    replied_by_followed: bool
    follower_count: int

def normalize_post(post:PostToRank):
    """
    Prepare a post to be used in the model by normalizing the values.
    Returns:
        ModelInput: Post with normalized values for the model.
    """
    return ModelInput(
        # Normalize engagement counts.
        like_count_normalized=np.log10(max(post.like_count,1))/5,
        reply_count_normalized=np.log10(max(post.reply_count,1))/5,
        click_count_normalized=np.log10(max(post.click_count,1))/5,
        # Convert ms to hours and normalize.
        age=post.age/1000/60/48,
        # Normalize engagement history counts.
        like_history_normalized=np.log10(max(post.like_history,1)),
        reply_history_normalized=np.log10(max(post.reply_history,1)),
        click_history_normalized=np.log10(max(post.click_history,1)),
        # Convert bools to float.
        followed=post.followed,
        replied_by_followed=post.replied_by_followed,
        # Normalize follower count.
        follower_count_normalized=np.log10(max(post.follower_count,1))/5,
        # Embedding similarity.
        embedding_similarity=post.embedding_similarity
    )
