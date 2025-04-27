import asyncpg
from src.common.env import settings

async def get_pool():
    return await asyncpg.create_pool(settings.db_url)