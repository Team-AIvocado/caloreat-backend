from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.food import Food
from app.db.models.nutrition import Nutrition


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

    # db에 없는 새로운 음식이름일 경우
    # TODO: foods, nutritions 테이블 통합 후 meal도메인쪽 서비스로 책임이관
    @staticmethod
    async def create_food_with_nutrition(
        db: AsyncSession, name: str, nutrition_data: dict
    ) -> Food:
        """
        음식 + 영양소 정보 동시 생성
        nutrition_data: {'calories': float, 'carbohydrate': float, 'protein': float, 'fat': float}
        """
        # 1. Food 생성
        db_food = Food(name=name)
        db.add(db_food)
        await db.flush()  # ID 생성을 위해 flush

        # 2. Nutrition 생성
        # TODO: App-wide Nutrition/Food table integration & ORM refactoring needed later
        db_nutrition = Nutrition(
            food_id=db_food.id,
            calories=nutrition_data.get("calories"),
            carbohydrate=nutrition_data.get("carbohydrate")
            or nutrition_data.get("carbs_g")
            or nutrition_data.get("carbs"),
            protein=nutrition_data.get("protein") or nutrition_data.get("protein_g"),
            fat=nutrition_data.get("fat") or nutrition_data.get("fat_g"),
        )
        db.add(db_nutrition)

        await db.commit()
        await db.refresh(db_food)
        return db_food
