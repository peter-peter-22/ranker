from typing import NamedTuple, List, Dict
from src.common.prepare_posts import separate_and_transform_posts, Engagement, RichPost
import asyncio
from operator import itemgetter
from src.common.fetch_data import EngagementType, get_tables
from src.common.normalize_post import PostToRank,normalize_post,ModelInput
from src.common.prepare_follows import get_follow_checker, FollowChecker
from sklearn.metrics.pairwise import cosine_similarity
from src.common.prepare_users import get_embedding_map
from src.common.engagement_history import engagement_history_manager, EngagementHistory
import numpy as np
from sklearn.model_selection import train_test_split
from dataclasses import dataclass, astuple

class EngagementEvent(NamedTuple):
    reply:bool
    like:bool
    click:bool

async def get_training_data():
    # Get the prepared posts and engagements
    print("Getting tables",flush=True)
    posts,likes,clicks,views,follows,users = await get_tables()

    # Get the rich post map
    print("Preparing posts",flush=True)
    post_map, replies = separate_and_transform_posts(posts)

    # Create the follow checker
    print("Preparing follows",flush=True)
    check_follow=get_follow_checker(follows)

    # Create the user embedding map
    print("Preparing users",flush=True)
    user_embedding_map = get_embedding_map(users)

    # Combine all engagements
    print("Merging engagements",flush=True)
    engagements = likes+replies+clicks+views

    # Sort all engagements by datetime
    print("Sorting engagements",flush=True)
    engagements.sort(key=lambda engagement: engagement.created_at)

    # Track the engagement history between the users
    get_engagement_history = engagement_history_manager()

    # List for storing all engagement events
    model_outputs:List[EngagementEvent] = []

    # List of processed posts and their relationship with the viewer
    model_inputs:List[ModelInput]=[]
        
    # Create model inputs and outputs from the engagements of the post.
    # Also calculate the engagement counts, engagement history and embedding vector in the process.
    print("Converting to training data",flush=True)
    for engagement in engagements:

        # Get the engaged post
        post=post_map.get(engagement.post_id)
        if not post:
            continue

        # Get the user embedding for the engagement
        user_embedding=user_embedding_map.get(engagement.user_id)
        if len(user_embedding)==0:
            continue

        # Get the engagement history between the viewer and the poster
        history=get_engagement_history(engagement.user_id,post.user_id)

        # Store data about the processed post
        model_inputs.append(normalize_post(create_input(engagement,post,user_embedding,check_follow,history)))

        # Create the engagement event
        model_outputs.append(create_output(engagement))

        # Update engagement metrics
        update_engagement_count(post,engagement)
        update_engagement_history(history,engagement)
    
    # Convert to np arrays
    print("Converting to np arrays",flush=True)
    print([len(el) for el in model_inputs])
    X=np.array(model_inputs)
    Y=np.array(model_outputs)

    # Split training data
    print("Splitting training data",flush=True)
    X_train,X_test,y_train,y_test=train_test_split(X,Y,test_size=0.2)
        
def update_engagement_count(post:RichPost,engagement:Engagement):
    """
    Update the engagement counts of a post based on an engagement event.
    """
    match engagement.type:
        case EngagementType.LIKE:
            post.like_count+=1
        case EngagementType.REPLY:
            post.reply_count+=1
        case EngagementType.CLICK:
            post.click_count+=1

def update_engagement_history(history:EngagementHistory,engagement:Engagement):
    """
    Update an engagement history based on an engagement event.
    """
    match engagement.type:
        case EngagementType.LIKE:
            history.likes+=1
        case EngagementType.REPLY:
            history.replies+=1
        case EngagementType.CLICK:
            history.clicks+=1


def create_output(engagement:Engagement):
    """Create a model output from an engagement."""
    return EngagementEvent(
        engagement.type == EngagementType.LIKE,
        engagement.type == EngagementType.REPLY,
        engagement.type == EngagementType.CLICK,
    )

def create_input(engagement:Engagement, post:RichPost, user_embedding:List[float], check_follow:FollowChecker, engagement_history:EngagementHistory):
    # Get the viewer
    viewer=engagement.user_id
    return PostToRank(
        # Get the engagement counts
        like_count=post.like_count,
        reply_count=post.reply_count,
        click_count=post.click_count,
        # Calculate the of the post when the engagement occured
        age=engagement.created_at - post.created_at,
        # Check if the viewer follows the publisher of the post.
        followed=check_follow(viewer,post.user_id),
        # Check if a user that the viewer follows replied to the post.
        replied_by_followed=any(check_follow(viewer, replier) for replier in post.repliers),
        # Calculate embedding similarity. TODO update per engagement?
        embedding_similarity=cosine_similarity([user_embedding],[post.embedding]),
        # Get the follower count of the poster TODO: implement
        follower_count=0,
        # Engagement history
        like_history=engagement_history.likes,
        reply_history=engagement_history.replies,
        click_history=engagement_history.clicks,
    )


asyncio.run(get_training_data())
