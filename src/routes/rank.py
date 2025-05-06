from fastapi import APIRouter

router = APIRouter()

# home page to check if the server works
@router.get("/rank")
async def rank():
    return"under construction"