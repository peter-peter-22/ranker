from fastapi import APIRouter

router = APIRouter()

@router.get("/train")
async def train():
    "hi"
