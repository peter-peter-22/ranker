from src.model.predict import PredictedEngagements

# How much the types of engagements worth when ranking posts
like_score=1
reply_score=2
click_score=0.5

def engagement_score(engagements:PredictedEngagements) -> float:
    """Score the engagements of a post."""
    return engagements.like_chance*like_score+engagements.reply_chance*reply_score+engagements.click_chance*click_score