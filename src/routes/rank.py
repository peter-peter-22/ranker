from fastapi import APIRouter
from pydantic import BaseModel
from src.common.fetch_data import PostToRank
from typing import List
from src.model.predict import predict
from src.model.score import engagement_score

router = APIRouter()

class RankerModel(BaseModel):
    posts: List[PostToRank]

# predict the scores of posts
@router.post("/rank")
async def rank(body:RankerModel):
    predicted_engagements=predict(body.posts)
    scores=list(map(engagement_score,predicted_engagements))
    return {"scores":scores,"predicted_engagements":predicted_engagements}