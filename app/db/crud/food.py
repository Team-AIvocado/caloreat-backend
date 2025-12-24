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
        # name -> foodname 변경
        result = await db.execute(
            select(Food).where(Food.foodname.ilike(f"%{query}%")).limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def create_food(db: AsyncSession, foodname: str, source: str = "llm") -> Food:
        """
        음식 생성 (Get-Or-Create 전략의 Create 부분)
        """
        # name -> foodname, source 추가
        db_food = Food(foodname=foodname, source=source)
        db.add(db_food)
        await db.commit()
        await db.refresh(db_food)
        return db_food

    # db에 없는 새로운 음식이름일 경우 create
    @staticmethod
    async def create_food_with_nutrition(
        db: AsyncSession,
        foodname: str,
        nutrition_data: dict,
        source: str = "llm",
    ) -> Food:
        """
        음식 + 영양소 정보 동시 생성
        nutrition_data: LLM output directly (carbs_g, protein_g, etc.)
        """
        # 1. Food 생성
        db_food = Food(foodname=foodname, source=source)
        db.add(db_food)
        await db.flush()  # ID 생성을 위해 flush

        # 2. Nutrition 생성
        # micronutrients 분리 (JSON 필드)
        micronutrients = nutrition_data.get("micronutrients", {})

        # 메인 영양소 필터링 (DB 모델에 있는 것만)
        # 단, micronutrients는 별도 컬럼이므로 nutrition_data에서 제외하고 넣거나 처리해야 함.

        # 딕셔너리 복사 후 micronutrients 키 제거 (별도 처리를 위해)
        clean_nutrition_data = nutrition_data.copy()
        if "micronutrients" in clean_nutrition_data:
            del clean_nutrition_data["micronutrients"]

        db_nutrition = Nutrition(
            food_id=db_food.id, micronutrients=micronutrients, **clean_nutrition_data
        )
        db.add(db_nutrition)

        await db.commit()
        await db.refresh(db_food)
        return db_food
