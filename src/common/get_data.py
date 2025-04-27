from src.common.db import get_pool
import asyncio
from typing import NamedTuple
from dataclasses import dataclass
from uuid import UUID

@dataclass
class Engagement:
    post_id:UUID
    user_id:UUID
    created_at:int

@dataclass
class Post:
    id:UUID
    user_id:UUID
    like_count:int
    reply_count:int
    click_count:int
    view_count:int
    created_at:int
    replying_to:UUID

async def get_tables():
    """
    Fetch and parse all engagements and related data.
    Returns: posts, likes, clicks, views
    """
    conn = await get_pool()

    async def get_likes():
        engagements = await conn.fetch('SELECT "postId","userId","createdAt" FROM likes LIMIT 10')
        return [Engagement(*row) for row in engagements]
    
    async def get_clicks():
        engagements = await conn.fetch('SELECT "postId","userId","createdAt" FROM clicks LIMIT 10')
        return [Engagement(*row) for row in engagements]

    async def get_views():
        engagements = await conn.fetch('SELECT "postId","userId","createdAt" FROM views LIMIT 10')
        return [Engagement(*row) for row in engagements]

    async def get_posts():
        posts=await conn.fetch('SELECT "id","userId","likeCount","replyCount","clickCount","viewCount","createdAt","replyingTo" from posts LIMIT 10')
        return [Post(*row) for row in posts]

    # Fetch in pararrel
    posts,likes,clicks,views=await asyncio.gather(
        get_posts(),
        get_likes(),
        get_clicks(),
        get_views()
    ) 
    
    await conn.close()
    
    return posts,likes,clicks,views