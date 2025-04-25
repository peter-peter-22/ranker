from src.common.db import get_pool
from fastapi import APIRouter

router = APIRouter()

@router.get("/train")
async def rank():
    async with get_pool().acquire() as conn:
        return await conn.fetchrow(
            'SELECT * FROM users LIMIT 1', 
        )
