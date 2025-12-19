from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.services.food import FoodService
from app.db.schemas.food import FoodRead

router = APIRouter(prefix="/foods", tags=["foods"])


@router.get("/search", response_model=list[FoodRead])
async def search_foods(
    q: str = Query(..., min_length=1, description="음식 검색어입력"),
    db: AsyncSession = Depends(get_db),
):
    """
    음식 검색 API
    - DB에서 'LIKE %query%' 검색
    - 결과가 없으면 빈 리스트 반환 (추후 LLM Fallback 확장 가능)
    """
    return await FoodService.search_food(db, q)
