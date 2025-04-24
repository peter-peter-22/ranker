import asyncpg
from contextlib import asynccontextmanager
from src.common.env import settings

pool:asyncpg.Pool = None

@asynccontextmanager
async def lifespan():
    pool = await asyncpg.create_pool(settings.db_url)
    yield
    pool.close()