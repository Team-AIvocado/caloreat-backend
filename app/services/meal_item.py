from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.clients.ai_client import AIClient
from app.db.models.food import Food
from app.db.models.nutrition import Nutrition
from app.db.schemas.nutrition_analysis import NutritionDetail
import uuid


class MealItemService:
    # AIClient.request_analysis 호출하여 음식 리스트에 대한 영양소 분석 및 반환
    # 음식에대한 영양소개념 < 내가먹은 식단에대한 영양소 스냅샷 개념 #### TODO: food에대한 영양소테이블은 이후 추가

    @staticmethod
    async def food_analysis(foodnames: list):
        """
        음식 리스트 -> AI 영양소 분석 요청
        foodnames: list[AnalysisItem]
        """
        # 1. 입력 데이터 가공
        # 프론트엔드에서 전달받은 image_id를 그대로 사용하여 매핑 유지
        # 1. 입력 데이터 가공
        # 프론트엔드에서 단순히 문자열 리스트로 오므로 UUID 생성하여 매핑
        foods_data = [
            {"id": str(uuid.uuid4()), "food_name": name} for name in foodnames
        ]

        # 2. AI 서버 요청 (Analysis)
        analysis_result = await AIClient.request_analysis(foods_data)

        # 3. 결과 반환
        return analysis_result

    # 음식한개
    @staticmethod
    async def one_food_analysis(db: AsyncSession, foodname: str):
        """
        음식명(Str) -> AI 영양소 분석 요청 (with Caching)
        """
        # 1. 캐시 조회
        cached_data = await MealItemService._get_food_from_cache(db, foodname)
        if cached_data:
            return cached_data

        # 2. AI 서버 요청
        analysis_result = await AIClient.request_single_analysis(foodname)

        # 3. 데이터 저장 및 캐싱
        await MealItemService._save_new_food_cache(db, foodname, analysis_result)

        # 4. 결과 반환
        return analysis_result

    # ================================================================
    # Private Helper Methods (Conflict Avoidance: Appended at bottom)
    # ================================================================

    @staticmethod
    async def _get_food_from_cache(db: AsyncSession, foodname: str):
        """
        [Private] 캐시(DB)에서 음식 정보 조회
        """
        stmt = select(Food).where(Food.name == foodname)
        result = await db.execute(stmt)
        food = result.scalar_one_or_none()  # TODO: 파일 및 로직분리필요

        if food and food.nutrition:
            # DB 데이터를 API 응답(Dict) 형태로 변환
            n = food.nutrition
            micronutrients = n.micronutrients if n.micronutrients else {}

            return {
                "foodname": food.name,
                "nutritions": {
                    "calories": n.calories,
                    "carbs_g": n.carbs_g,
                    "protein_g": n.protein_g,
                    "fat_g": n.fat_g,
                    "sugar_g": n.sugar_g,
                    "fiber_g": n.fiber_g,
                    "sodium_mg": n.sodium_mg,
                    "cholesterol_mg": n.cholesterol_mg,
                    "saturated_fat_g": n.saturated_fat_g,
                    "micronutrients": micronutrients,
                },
            }
        return None

    @staticmethod
    async def _save_new_food_cache(db: AsyncSession, foodname: str, llm_result: dict):
        """
        [Private] LLM 응답을 DB에 저장 (캐싱)
        """
        nutritions_data = llm_result.get("nutritions", {})

        try:
            parsed_nutrition = NutritionDetail(**nutritions_data)
        except Exception:
            # 파싱 실패 시 캐싱만 건너뛰고 결과 반환
            return llm_result

        new_food = Food(name=foodname)
        db.add(new_food)
        await db.flush()

        new_nutrition = Nutrition(
            food_id=new_food.id,
            source="LLM",
            calories=parsed_nutrition.calories,
            carbs_g=parsed_nutrition.carbs_g,
            protein_g=parsed_nutrition.protein_g,
            fat_g=parsed_nutrition.fat_g,
            sugar_g=parsed_nutrition.sugar_g,
            fiber_g=parsed_nutrition.fiber_g,
            sodium_mg=parsed_nutrition.sodium_mg,
            cholesterol_mg=parsed_nutrition.cholesterol_mg,
            saturated_fat_g=parsed_nutrition.saturated_fat_g,
            micronutrients=parsed_nutrition.micronutrients.model_dump(),
        )

        db.add(new_nutrition)
        await db.commit()
        await db.refresh(new_food)

        return llm_result

    # TODO: food도메인 추가 후 food tables db저장 로직 추가 필요 (MVP범위) ->
    # 중요 ★☆★☆★☆★☆★☆★☆★☆★☆★☆★☆★☆★☆★☆★☆★☆★☆★☆★☆
    # ... (기존 주석 보존)
    # food도메인 현재 존재 x
    # Food : 음식별 -영양소, 이름,한글이름, 스냅샷을 정규화한 테이블사용
    # 음식의 표준 영양 정보와 메타데이터를 제공하는 마스터 기준 정보(Master Data)
    # 역할: 중복된 외부 API 호출을 줄이고 데이터 일관성을 유지하기 위한 캐싱 및 기준값 제공

    # 각 모델별 초기 라벨값도 food 도메인에 포함
    # 이유: 동일한 음식에 대해 여러 모델이 서로 다른 라벨(Label)을 사용하더라도, 데이터의 유일성과 영양 정보의 일관성을 보장하기 위함

    # 결론: 반정규화 전략으로 진행
    # 향후 정규화 가능성을 해치지 않는선에서 도메인 결합
    # 쿼리복잡도증가, 기능구현우선, 현재 기능스코프 구현을 위해서는 반정규화로 구현난이도를 낮춰야함
    # AI데이터의 불확실성 (llm 반환값 신뢰도문제)
