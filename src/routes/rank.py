from fastapi import APIRouter
from src.common.db import pool

router = APIRouter()

# home page to check if the server works
@router.get("/rank")
async def rank():
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            'SELECT * FROM users LIMIT 1s', 
        )