from app.clients.ai_client import AIClient
from app.services.food import FoodService
import uuid
import asyncio
from app.db.schemas.nutrition_analysis import AnalysisItem
from app.db.schemas.nutrition_analysis import MultiAnalysisResponse


class MealItemService:
    # AIClient.request_analysis 호출하여 음식 리스트에 대한 영양소 분석 및 반환
    # 음식에대한 영양소개념 < 내가먹은 식단에대한 영양소 스냅샷 개념
    # TODO: 역할과 모듈 위치가 불일치함 food 도메인 생성됐으므로 이관필요
    @staticmethod
    async def food_analysis(db, foodnames: list[AnalysisItem]):
        """
        음식 리스트 -> AI 영양소 분석 요청
        with DB Cache & Auto-Save
        foodnames: list[AnalysisItem]
        """
        # 1. 입력 데이터 가공
        # 프론트엔드에서 전달받은 image_id를 그대로 사용하여 매핑 유지
        foods_data = [
            {"id": item.image_id, "food_name": item.foodname} for item in foodnames
        ]

        # 2. 개별 분석 요청 병렬 처리 (DB 확인 -> 없으면 AI -> 저장)
        # FoodService.get_or_create_food_from_analysis 내부에서 모든 로직 수행
        tasks = [
            FoodService.get_or_create_food_from_analysis(db, item["food_name"])
            for item in foods_data
        ]

        # 순서 보장되어 반환됨
        analysis_results = await asyncio.gather(*tasks)

        # 3. 결과 조립 (Assembly)
        assembled_results = []

        for original, result in zip(foods_data, analysis_results):
            # result는 {"foodname": ..., "nutritions": ...} 형태 (FoodService 반환값)
            item = result.copy()
            item["image_id"] = original["id"]  # ID 주입
            assembled_results.append(item)

        return MultiAnalysisResponse(results=assembled_results)

    # 음식한개 #TODO: 작동확인 후 주석처리 or 삭제예정 food_analysis로 통합
    @staticmethod
    async def one_food_analysis(db, foodname: str):
        """
        음식명(Str) -> AI 영양소 분석 요청
        with DB Cache & Defense Logic
        """
        return await FoodService.get_or_create_food_from_analysis(db, foodname)
