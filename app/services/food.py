from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.food import Food


from app.db.crud.food import FoodCrud
from app.clients.ai_client import AIClient


class FoodService:
    @staticmethod
    async def search_food(db: AsyncSession, query: str) -> list[Food]:
        """
        음식 검색
        Service: ORM 객체 반환 -> Router: Pydantic 검증
        """
        # 1. DB 검색 (Happy Path)
        return await FoodCrud.get_foods_by_name(db, query)

    @staticmethod
    def validate_food_name(name: str) -> bool:
        """
        AI 요청 전 1차 입력 검증
        - 최소 1글자 이상 (한글 기준, 영어는 2글자?) -> 일단 길이 1 이상 허용
        - 최대 길이 20자 제한 (악의적 긴 입력 방지)
        - 불필요한 특수문자만 있는 경우 등 필터링
        """
        if not name or not name.strip():
            return False

        cleaned = name.strip()
        if len(cleaned) > 30:  # 넉넉하게 30자
            return False

        # TODO: 욕설, ㅋㅋㅋ 등 필터링 로직 추가 가능

        return True

    @staticmethod
    async def get_or_create_food_from_analysis(db: AsyncSession, foodname: str):
        """
        [Isolated Logic] 음식 분석 및 저장
        Refactored to Main Flow:
        1. DB Check (Exact Match)
        2. LLM Analysis (with Defense)
        3. Save (Standardized)
        """
        # 1. DB 재조회 (Exact Match)
        if existing := await FoodService._get_existing_food_response(db, foodname):
            return existing

        # 2. LLM 분석 및 유효성 검증
        analysis_result = await FoodService._analyze_and_validate(foodname)

        # 유효하지 않은 결과(빈 딕셔너리 등)면 바로 반환
        if not analysis_result.get("nutritions"):
            return analysis_result

        # 3. DB 저장 (Standardized Name)
        return await FoodService._save_standardized_food(db, analysis_result)

    # --- Helper Methods ---

    @staticmethod
    async def _get_existing_food_response(db: AsyncSession, name: str):
        """DB에서 정확히 일치하는 음식을 찾아 응답 포맷으로 반환"""
        existing_foods = await FoodCrud.get_foods_by_name(db, name)
        for food in existing_foods:
            if food.name == name:
                return {
                    "foodname": food.name,
                    "nutritions": {
                        "calories": food.nutrition.calories if food.nutrition else 0,
                        "carbs": food.nutrition.carbohydrate if food.nutrition else 0,
                        "protein": food.nutrition.protein if food.nutrition else 0,
                        "fat": food.nutrition.fat if food.nutrition else 0,
                    },
                }
        return None

    @staticmethod
    async def _analyze_and_validate(foodname: str) -> dict:
        """LLM 분석 요청 및 Input/Output 방어 로직 수행"""
        # 1. Input Defense (1차)
        if not FoodService.validate_food_name(foodname):
            return {"foodname": foodname, "nutritions": {}}

        # 2. Analysis Request
        analysis_result = await AIClient.request_single_analysis(foodname)

        # 3. Output Validation (2차)
        # Type Check & Extraction
        if hasattr(analysis_result, "nutritions"):
            nutritions = analysis_result.nutritions
            corrected_name = analysis_result.foodname
        else:
            nutritions = analysis_result.get("nutritions", {})
            corrected_name = analysis_result.get("foodname", foodname)

        # Data Integrity Check (Zero check)
        is_valid_food = any(
            float(nutritions.get(k, 0) or 0) > 0
            for k in ["calories", "carbs", "protein", "fat"]
        ) and all(
            float(nutritions.get(k, 0) or 0) >= 0
            for k in ["calories", "carbs", "protein", "fat"]
        )

        if not is_valid_food:
            return {"foodname": foodname, "nutritions": {}}

        # Return valid dictionary for next step
        return {
            "foodname": corrected_name,  # Standardized name from LLM
            "nutritions": nutritions,
        }

    @staticmethod
    async def _save_standardized_food(db: AsyncSession, analysis_data: dict):
        """정제된 이름으로 중복 체크 후 저장"""
        corrected_name = analysis_data["foodname"]
        nutritions = analysis_data["nutritions"]

        # 4-1. 저장 전, 정제된 이름으로 재확인 (Race Condition / Synonym 방어)
        # 예: "떡뽂이"(Input) -> "떡볶이"(Analyzed) -> DB에 "떡볶이"가 있는지 확인
        if existing := await FoodService._get_existing_food_response(
            db, corrected_name
        ):
            return existing

        # 4-2. 최종 저장
        await FoodCrud.create_food_with_nutrition(db, corrected_name, nutritions)

        return analysis_data
