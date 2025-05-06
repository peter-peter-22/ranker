from fastapi import APIRouter
from typing import NamedTuple
from src.common.fetch_data import get_all_engagements
from src.common.prepare_posts import separate_and_transform_posts
import asyncio

router = APIRouter()

@router.get("/train")
async def train():
    "hi"
