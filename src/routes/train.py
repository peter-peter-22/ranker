from fastapi import APIRouter
from typing import NamedTuple
from src.common.get_data import get_tables
from src.common.prepare_data import prepare_posts
import asyncio

router = APIRouter()

@router.get("/train")
async def train():
    posts,likes,clicks,views = await get_tables()
    post_map,replies=prepare_posts(posts)
    print(post_map)

asyncio.run(train())