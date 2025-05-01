from src.common.db import get_pool
import asyncio
from dataclasses import dataclass
from uuid import UUID
from enum import Enum, auto
from typing import List, NamedTuple

class EngagementType(Enum):
    LIKE = auto()
    REPLY = auto()
    CLICK = auto()
    VIEW = auto()

@dataclass
class Engagement:
    post_id:UUID
    user_id:UUID
    created_at:int
    type: EngagementType

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
    embedding:List[float]

class Follow(NamedTuple):
    follower:UUID
    followed:UUID

class User(NamedTuple):
    id:UUID
    embedding:List[float]

async def get_tables():
    """
    Fetch and parse all engagements and related data.
    Returns:
        posts, likes, clicks, views, follows, users
    """
    conn = await get_pool()

    async def get_likes():
        engagements = await conn.fetch('SELECT "postId","userId","createdAt" FROM likes')
        return [Engagement(*row,type=EngagementType.LIKE) for row in engagements]
    
    async def get_clicks():
        engagements = await conn.fetch('SELECT "postId","userId","createdAt" FROM clicks')
        return [Engagement(*row,type=EngagementType.CLICK) for row in engagements]

    async def get_views():
        engagements = await conn.fetch('SELECT "postId","userId","createdAt" FROM views')
        return [Engagement(*row,type=EngagementType.VIEW) for row in engagements]

    async def get_posts():
        posts=await conn.fetch('SELECT "id","userId","likeCount","replyCount","clickCount","viewCount","createdAt","replyingTo","embedding" from posts')
        return [Post(*row) for row in posts]
    
    async def get_follows():
        follows=await conn.fetch('SELECT "followerId","followedId" from follows')
        return [Follow(*row) for row in follows]
    
    async def get_users():
        user=await conn.fetch('SELECT "id","embedding" from users')
        return [User(*row) for row in user]

    # Fetch in pararrel
    posts,likes,clicks,views,follows,users=await asyncio.gather(
        get_posts(),
        get_likes(),
        get_clicks(),
        get_views(),
        get_follows(),
        get_users()
    ) 
    
    await conn.close()
    
    return posts,likes,clicks,views,follows,users