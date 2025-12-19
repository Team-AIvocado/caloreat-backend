from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.food import Food


from app.db.crud.food import FoodCrud


class FoodService:
    @staticmethod
    async def search_food(db: AsyncSession, query: str) -> list[Food]:
        """
        음식 검색
        Service: ORM 객체 반환 -> Router: Pydantic 검증
        """
        # 1. DB 검색 (Happy Path)
        return await FoodCrud.get_foods_by_name(db, query)

    # llm 넘길때 필터링할 함수
