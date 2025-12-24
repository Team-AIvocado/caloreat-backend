from app.clients.ai_client import AIClient
from app.services.food import FoodService
import uuid


class MealItemService:
    # AIClient.request_analysis 호출하여 음식 리스트에 대한 영양소 분석 및 반환
    # 음식에대한 영양소개념 < 내가먹은 식단에대한 영양소 스냅샷 개념
    # TODO: 역할과 모듈 위치가 불일치함 food 도메인 생성됐으므로 이관필요
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
    async def one_food_analysis(db, foodname: str):
        """
        음식명(Str) -> AI 영양소 분석 요청
        with DB Cache & Defense Logic
        """
        return await FoodService.get_or_create_food_from_analysis(db, foodname)
