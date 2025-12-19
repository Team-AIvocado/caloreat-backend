from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.food import Food


class FoodCrud:
    @staticmethod
    async def get_foods_by_name(
        db: AsyncSession, query: str, limit: int = 50
    ) -> list[Food]:
        """
        음식 이름 검색 (ILIKE)
        """
        result = await db.execute(
            select(Food).where(Food.name.ilike(f"%{query}%")).limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def create_food(db: AsyncSession, name: str) -> Food:
        """
        음식 생성 (Get-Or-Create 전략의 Create 부분)
        """
        db_food = Food(name=name)
        db.add(db_food)
        await db.commit()
        await db.refresh(db_food)
        return db_food
