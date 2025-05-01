from src.common.fetch_data import User
from typing import List

def get_embedding_map(users:List[User]):
    """
    Create a map of embedding vectors from the users where the key is the user id and the value is the embedding vector.
    Returns:
        Dict[UUID,Embedding]: A dictionary mapping user IDs to their corresponding embedding vectors.
    """
    return {user.id:user.embedding for user in users}
