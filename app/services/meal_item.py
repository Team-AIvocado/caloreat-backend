from app.clients.ai_client import AIClient
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
    async def one_food_analysis(foodname: str):
        """
        음식명(Str) -> AI 영양소 분석 요청
        """
        # 2. AI 서버 요청 (Analysis)
        analysis_result = await AIClient.request_single_analysis(foodname)

        # 3. 결과 반환
        return analysis_result

    # TODO: food도메인 추가 후 food tables db저장 로직 추가 필요 (MVP범위) ->
    # 중요 ★☆★☆★☆★☆★☆★☆★☆★☆★☆★☆★☆★☆★☆★☆★☆★☆★☆★☆
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
