import asyncpg
from src.common.env import settings
from pgvector.asyncpg import register_vector

async def get_pool():
    # Create connection, add the converters
    pool=await asyncpg.create_pool(settings.db_url,init=register_vector)
    return pool