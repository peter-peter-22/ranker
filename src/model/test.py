from src.common.db import get_pool
from src.common.fetch_data import post_subset, PostToRank, Engagements
from src.model.predict import predict, PredictedEngagements
import asyncio
from tabulate import tabulate
from typing import NamedTuple,List
from src.model.score import engagement_score

class TestPost(NamedTuple):
    post:PostToRank
    real:Engagements
    predicted:PredictedEngagements
    score:float

async def test_model():
    """Rank posts with the model and display metadata for testing"""
    # Get posts
    posts=await get_scored_posts()
    # Display
    display(posts)

async def get_scored_posts():
    """Get posts with predicted and real engagements sorted by score"""
    posts,real,predicted=await get_test_data()
    return transform_posts(posts,real,predicted)


async def get_test_data():
    """Get posts with real and predicted engagements"""
    tested_posts=1000

    pool = await get_pool()
    # Count total views
    count=(await pool.fetch(f"select count(*) from views"))[0][0]
    # Get a random subset of rankable posts
    posts,engagements=await post_subset(count,tested_posts,pool)
    # Make predictions
    predictions=predict(posts)
    await pool.close()
    # Return data
    return posts,engagements,predictions

def transform_posts(posts,real,predicted):
    """Format and sort the posts and their data"""
    # Format and calculate score
    merged=[TestPost(*test_post,engagement_score(test_post[2])) for test_post in zip(posts,real,predicted)]
    # Sort by score
    merged=sorted(merged,key=lambda test_post:test_post.score,reverse=True)
    return merged

def display(test_posts:List[TestPost]):
    header=("Scr","LC", "RC", "CC", "Age", "ES", "LH","RH","CH","F","RbF","RE","PE")
    rows=[header]
    rows.extend(
        map(
            lambda x: (
                f"{x.score:.2f}",
                x.post.like_count,
                x.post.reply_count,
                x.post.click_count,
                f"{x.post.age:.0f}",
                f"{x.post.embedding_similarity:.2f}",
                x.post.like_history,
                x.post.reply_history,
                x.post.click_history,
                x.post.followed,
                x.post.replied_by_followed,
                [int(e) for e in x.real],
                [f"{e:.2f}" for e in x.predicted]
            ),
            test_posts
        )
    )
    print(tabulate(rows))
        

asyncio.run(test_model())