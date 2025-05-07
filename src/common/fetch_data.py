from src.common.db import get_pool
from typing import NamedTuple, List
from datetime import timedelta
from src.common.query import get_query
import math
import asyncpg
import random
import asyncio

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

def training_data_fetcher():
    """
    Export functions to fetch training data in batches, and validation data.

    Returns:
        init: function to create database connection and batches
        get_data: generator function to fetch training data in batches
        close: function to close the database connection
        get_validation_data: function to get a set of training data to validate

    """
    batches:list[Batch]=None
    pool:asyncpg.Pool=None
    batch_size=100_000
    validation_size=200_000
    processes=2
    count:int=None

    # Create pool, count the rows and create batches
    async def init():
        nonlocal batches,pool,batch_size,count

        print("Preparing training data fetcher",flush=True)

        # Count rows
        pool = await get_pool()
        count=(await pool.fetch(f"select count(*) from views"))[0][0]
        print(f"Found {count} rows",flush=True)

        # Create batches
        batches=[Batch(batch_size,i*batch_size) for i in range(math.ceil(count/batch_size))]
        print(f"Created {len(batches)} batches",flush=True)

    # Get validation data
    async def validation_data():
        nonlocal pool, count
        return await post_subset(count,validation_size,pool)

    # Generator function to return shuffled batches of data.
    async def get_data():
        nonlocal batches,pool
        
        # Shuffle the batches
        random.shuffle(batches)
        # Collect the indexes of the remaining batches
        remaining_batches=list(range(len(batches)))
        # Create query
        query=get_query("select * from views offset $1 limit $2")
        # Create task list
        tasks:List[asyncio.Task[List]]=[]

        # Process each batch
        while len(tasks) + len(remaining_batches) > 0:

            # Create tasks to match the target pararrel process count
            while len(tasks)<processes and len(remaining_batches)>0:
                # Select the index of the first unprocessed batch
                selected_batch_index=remaining_batches.pop(0)
                print(f"Fetching batch {selected_batch_index+1}",flush=True)
                # Select the first unprocessed batch
                selected_batch=batches[selected_batch_index]
                # Create a task to fetch the selected batch
                tasks.append(asyncio.create_task(
                    pool.fetch(query,selected_batch.offset,selected_batch.limit)
                ))

            # Get current batch number
            batch_number=len(batches)-(len(remaining_batches)+len(tasks))+1
            # Wait for the first task to finish
            print(f"Waiting for batch {batch_number}/{len(batches)} to complete",flush=True)
            rows=await tasks.pop(0)
            print(f"Batch {batch_number}/{len(batches)} completed",flush=True)
            # Shuffle the rows
            random.shuffle(rows)
            # Format and return the rows
            yield format_rows(rows)

    # Close the pool
    async def close():
        nonlocal pool

        if(pool!=None):
            await pool.close()
        print("Datastream closed",flush=True)

    return init,get_data,close,validation_data

def format_rows(rows:List):
    """
    Convert database rows into types.

    Args:
        rows (List): A list of database rows.

    Returns:
        posts (List[PostToRank]): A list of rankable posts.
        engagements (List[Engagements]): A list of engagements.
    """
    # Format the rows
    posts=[PostToRank(*row[:10]) for row in rows]
    engagements=[Engagements(*row[10:]) for row in rows]
    return posts,engagements

async def post_subset(total_count:int,target_count:int,pool:asyncpg.Pool):
    """
    Fetch a random subset of the engaged posts.

    Args:
        total_count (int): Total number of posts.
        target_count (int): Number of posts to be fetched.
        pool (asyncpg.Pool): Database connection pool.

    Returns:
        posts (List[PostToRank]): A list of rankable posts.
        engagements (List[Engagements]): A list of engagements.
    """
    # Calculate how much percent of the table is the target
    percent=target_count/total_count*100
    print(f"Fetching the {percent:.4f}% of {total_count} rows.",flush=True)

    # Create query to fetch 
    query=get_query(f"select * from views tablesample bernoulli({percent}) repeatable(100)")

    # Fetch rows
    rows=await pool.fetch(query)
    print(f"Fetched {len(rows)} rows.",flush=True)
    
    # Format and return rows
    return format_rows(rows)
