from src.common.get_data import Post,Engagement
from typing import List,Set,Dict
from dataclasses import dataclass
from uuid import UUID

@dataclass
class RichPost(Post):
    repliers:Set[str]

def prepare_posts(posts:List[Post])->tuple[Dict[str,RichPost],List[Engagement]]:
    """
    Separate and transform posts and replies.
    Returns: post map and replies.
    """
    # Separate posts and replies
    replies,not_replies=separate(posts)
    # Create map of rich posts where the id is the key
    post_map:Dict[UUID,RichPost] = {post.id: RichPost(**vars(post),repliers=set()) for post in not_replies}
    # Add the id of the unique replies to the posts
    add_repliers(post_map,replies)
    return post_map,Engagement


def separate(posts:List[Post]):
    """
    Separate posts and replies.
    Returns: replies, not_replies
    """
    replies:List[Engagement]=[]
    not_replies:List[Post]=[]
    for post in posts:
        if post.replying_to:
            # Format the reply as engagement
            replies.append(Engagement(post.replying_to,post.user_id,post.created_at))
        else:
            not_replies.append(post)
    return replies,not_replies

def add_repliers(post_map:Dict[str,RichPost],replies:List[Engagement]):
    """
    Add the id of the unique repliers to the posts.
    """
    for reply in replies:
        post=post_map.get(reply.post_id)
        if not post:
            continue
        post.repliers.add(reply.user_id)

    