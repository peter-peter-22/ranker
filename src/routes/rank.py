from fastapi import APIRouter

router = APIRouter()

# home page to check if the server works
@router.get("/rank")
def rank():
    return "Hello from Python!"