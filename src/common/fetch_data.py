from src.common.db import get_pool
import asyncio
from dataclasses import dataclass
from uuid import UUID
from enum import Enum, auto
from typing import List, NamedTuple, Tuple
from datetime import timedelta
import asyncpg

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

async def get_tables():
    conn = await get_pool()

	# Get the posts and engagements
    categories=await asyncio.gather(
        get_activity(conn,"likes","postId","userId","createdAt",Engagements(True,False,False)),
		get_activity(conn,"likes","postId","userId","createdAt",Engagements(True,False,False)),
        get_activity(conn,"likes","postId","userId","createdAt",Engagements(True,False,False)),
        get_activity(conn,"likes","postId","userId","createdAt",Engagements(True,False,False))
	)
    
    await conn.close()
    
	# Merge the lists
    posts=[post for category in categories for post in category[0]]
    engagements=[post for category in categories for post in category[1]]
    
    return posts,engagements
    
async def get_activity(conn:asyncpg.Pool,table_name:str,post_column:str,viewer_column:str,timestamp_column:str,engagement_type:Engagements)->Tuple[List[PostToRank],List[Engagements]]:
    """
    Get the posts with historical data paired with their engagement.  
    
	Args:
		conn (Pool): The database pool.
        table_name (str): The name of the engagement table.
        post_column (str): The name of the engaged post id column in the engagement table.
        viewer_column (str): The name of the viewer column in the engagement table.
        timestamp_column (str): The name of the timestamp column on the engagement table.
        engagement_type (Engagements): The type of engagement the table contains.
    
    Returns:
		List[PostToRank]: The engagements paired with t
    """
    
	# Create the query
    query=f"""
select 
	-- The age of the post when it was engaged
	engagement."{timestamp_column}" - post."createdAt" as age,
	-- Post engagement counts
	coalesce(post_snapshot."likeCount",0) as engagement,
	coalesce(post_snapshot."replyCount",0) as replies,
	coalesce(post_snapshot."clickCount",0) as clicks,
	-- Embedding similarity between the user and the post
	coalesce(1 - (post.embedding <=> users.embedding), 0)::real as cosine_similarity,
	-- Engagement history between the viewer and the poster
	coalesce(history."likeCount",0) as like_history,
	coalesce(history."replyCount",0) as reply_history,
	coalesce(history."clickCount",0) as click_history,
	-- Historical following status
	coalesce(follow_snapshot."isFollowing",false) as followed,
	-- Check if the engaged post was replied by a followed user
	exists(
		select * from posts reply
		-- Check of the publisher of the reply was followed when the engagement happened
		inner join lateral (
			select * from follow_snapshots reply_follow_snapshot
			where 
				reply_follow_snapshot."followerId"=engagement."{viewer_column}"
				and
				reply_follow_snapshot."followerId"=post."userId" 			
				and 
				reply_follow_snapshot."createdAt"<engagement."{timestamp_column}"  
			order by follow_snapshot."createdAt" desc
			limit 1
		) reply_follow_snapshot on true
		-- Check if the reply is replying to the post and it was created before the engagement
		where 
			reply."replyingTo"=post.id
			and 
			reply."createdAt"<engagement."{timestamp_column}"
			and
			reply_follow_snapshot."isFollowing"
	) as replied_by_followed
-- Start with the engagements
from {table_name} engagement
-- Add the interacted post
left join posts post on post.id=engagement."{post_column}"
-- Add the add the user who created the engagement
left join users on users.id=engagement."{viewer_column}"
-- Add the lastest post snapshot before the engagement was created
left join lateral (
	select * from post_snapshots 
	where 
		engagement."{post_column}"=post_snapshots."postId" 
		and 
		post_snapshots."createdAt"<engagement."{timestamp_column}"  
	order by post_snapshots."createdAt" desc
	limit 1
) post_snapshot on true
-- Add the lastest engagement history snapshot before the engagement was created
left join lateral (
	select * from engagement_history_snapshots history
	where 
		history."viewerId"=engagement."{viewer_column}" 
		and 
		post."userId"=history."posterId" 
		and 
		history."createdAt"<engagement."{timestamp_column}"  
	order by history."createdAt" desc
	limit 1
) history on true
-- Add the lastest follow snapshot before the engagement was created
left join lateral (
	select * from follow_snapshots follow_snapshot
	where 
		follow_snapshot."followerId"=engagement."{viewer_column}" 
		and 
		post."userId"=follow_snapshot."followedId" 
		and 
		follow_snapshot."createdAt"<engagement."{timestamp_column}"  
	order by follow_snapshot."createdAt" desc
	limit 1
) follow_snapshot on true
limit 100
    """
    
	# Fetch the rows
    rows=await conn.fetch(query)
    
    # Format the rows
    posts=[PostToRank(*row) for row in rows]
    engagements=[engagement_type for _ in range(len(posts))]
    
    return posts,engagements
	
asyncio.run(get_tables())