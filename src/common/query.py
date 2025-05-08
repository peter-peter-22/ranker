def get_query(base_table_selector:str):
    """
    Create a query to get all engaged posts with their historical data and engagement types.
    
    Args:
	    base_table_selector (str): A part of the views table.
            
    Returns:
        str: The query string.
    """
    return f"""
select 
	-- The age of the post when it was engaged
	extract(epoch from view."createdAt" - post."createdAt")/3600 as age,
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
		-- Check if the publisher of the reply was followed when the engagement happened
		inner join lateral (
			select * from follow_snapshots reply_follow_snapshot
			where 
				reply_follow_snapshot."followerId"=view."userId"
				and
				reply_follow_snapshot."followerId"=post."userId" 			
				and 
				reply_follow_snapshot."createdAt"<view."createdAt"  
			order by follow_snapshot."createdAt" desc
			limit 1
		) reply_follow_snapshot on true
		-- Check if the reply is replying to the post and it was created before the engagement
		where 
			reply."replyingTo"=post.id
			and 
			reply."createdAt"<view."createdAt"
			and
			reply_follow_snapshot."isFollowing"
	) as replied_by_followed,
	-- Get all engagements between the viewer and the post
	-- Like
	exists(
		select * from likes 
		where likes."userId"=view."userId" and likes."postId"=view."postId"
	) as liked,
	-- Reply
	exists(
		select * from posts replies 
		where replies."userId"=view."userId" and replies."replyingTo"=view."postId"
	) as replied,
	-- Click
	exists(
		select * from clicks 
		where clicks."userId"=view."userId" and clicks."postId"=view."postId"
	) as liked
-- Get the views
from ({base_table_selector}) view
-- Add the interacted post
inner join posts post on post.id=view."postId"
-- Add the add the viewer user
inner join users on users.id=view."userId"
-- Get the closest snapshots to the time when the user seen the post
-- Post engagement counts snapshot
left join lateral (
	select * from post_snapshots 
	where 
		view."postId"=post_snapshots."postId" 
		and 
		post_snapshots."createdAt"<view."createdAt"  
	order by post_snapshots."createdAt" desc
	limit 1
) post_snapshot on true
-- User engagement history snapshot
left join lateral (
	select * from engagement_history_snapshots history
	where 
		history."viewerId"=view."userId" 
		and 
		post."userId"=history."posterId" 
		and 
		history."createdAt"<view."createdAt"  
	order by history."createdAt" desc
	limit 1
) history on true
-- Follow snapshot
left join lateral (
	select * from follow_snapshots follow_snapshot
	where 
		follow_snapshot."followerId"=view."userId" 
		and 
		post."userId"=follow_snapshot."followedId" 
		and 
		follow_snapshot."createdAt"<view."createdAt"  
	order by follow_snapshot."createdAt" desc
	limit 1
) follow_snapshot on true
    """