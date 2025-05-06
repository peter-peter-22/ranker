from src.common.db import get_pool
from src.common.fetch_data import post_subset
from src.model.predict import predict
import asyncio

async def test_model():
    # Get posts with real and predicted engagements
    posts,real,predicted=await get_test_data()
    
    

async def get_test_data():
    tested_posts=100

    pool = await get_pool()
    # Count total views
    count=(await pool.fetch(f"select count(*) from views"))[0][0]
    # Get a random subset of rankable posts
    posts,engagements=await post_subset(count,tested_posts,pool)
    predictions=predict(posts)
    # Return data
    posts,engagements,predictions
    
asyncio.run(get_test_data())