from src.common.db import get_pool
from typing import NamedTuple
from datetime import timedelta
from src.common.query import get_query
import math
import asyncpg
import random


class PostToRank(NamedTuple):
    """
    All data for of a post that the model will process.
    """
    age: timedelta    
    like_count: int
    reply_count: int
    click_count: int
    embedding_similarity: float
    like_history: int
    reply_history: int
    click_history: int
    followed: bool
    replied_by_followed: bool
    
class Engagements(NamedTuple):
    """
    The engagements of a post.
    """
    liked: bool
    replied: bool
    clicked: bool
    
class Batch(NamedTuple):
    """
    The boundaries of a batch to be processed.
    """
    limit: int
    offset: int

def create_data_stream():
    batches:list[Batch]=None
    pool:asyncpg.Pool=None
    batch_size=10_000

    # Create pool, count the rows and create batches
    async def init():
        nonlocal batches,pool,batch_size

        print("Preparing training data stream",flush=True)

        # Count rows
        pool = await get_pool()
        count=(await pool.fetch(f"select count(*) from views"))[0][0]
        print(f"Found {count} rows",flush=True)

        # Create batches
        batches=[Batch(batch_size,i*batch_size) for i in range(math.ceil(count/batch_size))]
        print(f"Created {len(batches)} batches",flush=True)
        return batches

    # Generator function to return shuffled batches of data.
    async def get_data():
        nonlocal batches,pool

        # Check if the initialization happened
        if(batches==None or pool==None):
            raise Exception("Data stream not initialized")
        
        # Shuffle the batches
        random.shuffle(batches)

        # Process each match
        for i,batch in enumerate(batches):
            print(f"Processing batch {i+1}/{len(batches)}",flush=True)
            # Get the rows
            rows=await pool.fetch(get_query(),batch.offset,batch.limit)
            # Shuffle the rows
            random.shuffle(rows)
            # Format the rows
            posts=[PostToRank(*row[:10]) for row in rows]
            engagements=[Engagements(*row[10:]) for row in rows]
            # Return the results
            yield posts,engagements

    # Close the pool
    async def close():
        nonlocal pool

        if(pool!=None):
            await pool.close()
        print("Datastream closed",flush=True)

    return init,get_data,close
