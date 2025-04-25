import asyncpg
from contextlib import asynccontextmanager
from src.common.env import settings
from fastapi import FastAPI

pool:asyncpg.Pool = None

@asynccontextmanager
async def lifespan(app:FastAPI):
    print("start")
    global pool
    pool = await asyncpg.create_pool(settings.db_url)
    yield 
    await pool.close()

def get_pool():
    return pool