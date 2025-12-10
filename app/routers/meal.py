from fastapi import APIRouter, Depends, status, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_user_id, get_current_user
from app.db.models import User
from app.db.database import get_db

# 스키마
from app.db.schemas.meal_image import MealImageResponse, OverrideResponse
from app.db.schemas.meal_log import (
    MealLogUpdate,
    MealLogRead,
    MealLogCreate,
)
from app.db.schemas.nutrition_analysis import (
    NutrientAnalysisResponse,
    AnalysisRequest,
    OverrideTextResponse,
    OverrideTextRequest,
)

import io
from datetime import date

# 서비스
from app.services.meal_image import MealImageService
from app.services.meal_item import MealItemService
from app.services.meal_log import MealLogService

# meal domain ux흐름 일치 엔드포인트끼리 묶음
# meal_log, meal_item, meal_image
# 이미지업로드 라우터에서 끝 /db저장 x (v1)

router = APIRouter(prefix="/meals", tags=["Meal"])


# 식단이미지 upload -> #TODO: (back-infer) request classification
# backend 파일 업로드 경로 img -> raw - tmp
# img 업로드 및 cls
@router.post("/upload", response_model=MealImageResponse)
async def upload_image_endpoint(
    current_user: User = Depends(get_current_user),
    file: UploadFile = File(None),
):
    # Service Skeleton 호출
    detection_result = await MealImageService.image_detection(file, current_user.id)
    return detection_result

    # # TODO: 임시 - Inference or LLM 모듈 호출 & Background Task - S3 저장 구현 필요
    # return {
    #     "image_id": "uuid",  # tmp 이미지식별용 프론트 반환 id
    #     "food_name": "된장찌개",  # response.candidates[0]["label"]
    #     "candidates": [
    #         {"label": "된장찌개", "confidence": 0.93},
    #         {"label": "김치찌개", "confidence": 0.72},
    #     ],
    # }


# foodname = front state 값 db 저장x


# --- input ---
## meal_image Upload / meal_image.py집합
# TODO: endpoint authentication 추가 필요 / S3 DDOS 공격 고려


# 사진 재촬영 업로드 - 중복업로드방지
@router.post("/override/image", response_model=OverrideResponse)
async def override_prediction_endpoint(
    current_user: User = Depends(get_current_user),
    file: UploadFile = File(None),
):
    # TODO: 사진 분석 임시 API hard coded (Inference or LLM 모듈과 연결되면 수정)
    return {
        "image_id": "uuid",  # tmp 이미지식별용 프론트 반환 id
        "food_name": "된장찌개",  # response.candidates[0]["label"]
        "candidates": [
            {"label": "된장찌개", "confidence": 0.93},
            {"label": "김치찌개", "confidence": 0.72},
        ],
        "corrected": True,
    }


# 텍스트 입력(수동입력) # post x -> get
# free-text 서비스 품질 박살 (ex. 떡볶이 / 떡복이 / 떡뽂이 / 떡볶기)
# 사용자 입력 문자열을 믿지말것
# TODO: 입력해도 안나올시 -> llm에 보내서 음식명 추출한다던지 대안필요
@router.get("/foods/manual")
async def search_foods_manual_endpoint(
    query: str,  # 사용자가 입력한 텍스트
    limit: int = 10,  # 반환 개수
    db: AsyncSession = Depends(get_db),
):
    """
    음식명 자동완성 검색 API
    GET /foods/search?query=된장
    examples = ["된장찌개", "된장국", "김치찌개", "김치볶음밥", "카레", "치킨", "김밥"]
    """

    # TODO: 실제 음식 DB 존재 시 SQL LIKE 검색 /
    # 예시 mock 데이터
    all_foods = ["된장찌개", "된장국", "김치찌개", "김치볶음밥", "카레", "치킨", "김밥"]

    # 필터링
    results = [f for f in all_foods if query in f][:limit]

    # 자동완성 리스트 반환
    return {"results": results}


# 음식 text 영양소분석
# 1단계 image detect/cls 에서 선택된 이미지 (아/점/저)
# 사용자확인 전단계가 존재하므로 confidence는 생략 foodname만 전달


# 한끼(점심)에 먹는 음식(str)이 여러개임
# inferserver request는 하나씩 낱개로
@router.post("/analyze", response_model=NutrientAnalysisResponse)
async def analyze_image_endpoint(foodnames: AnalysisRequest):
    # Service Skeleton 호출
    return await MealItemService.food_analysis(foodnames.foods)

    # # TODO: 임시 - DB 검색 & 없는경우 LLM Module 호출
    # return {
    #     "results": [
    #         {"foodname": "된장찌개", "nutritions": {"calories": 230, "carbs": 18}},
    #         {"foodname": "김치", "nutritions": {"calories": 90, "carbs": 7}},
    #     ]
    # }  # nutiritionsta


# ===================================================
# output & meal_log, item crud


# 식단저장
@router.post("/log")
async def create_meal_log_endpoint(
    meal: MealLogCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    create_meal_log_endpoint
    meal_type: breakfast, launch, dinner, snack(opt.)
    """
    # Service Skeleton 호출
    return await MealLogService.create_meal_log(db, meal, current_user.id)

    # # TODO: 임시 - DB 저장 구현 필요
    # return {
    #     "meal_type": "snack",
    #     "eaten_at": "2025-12-04T15:09:50.409Z",
    #     "meal_items": [
    #         {
    #             "foodname": "avocado",
    #             "quantity": 100,
    #             "nutritions": {"calories": 90, "carbs": 7, "fat": 999},
    #         }
    #     ],
    # }


# read by date/ query
@router.get("/logs", response_model=list[MealLogRead])
async def read_meal_log_endpoint(
    date: date | None = None,  # query param
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    ?date=2025-12-04
    example request : 2025-12-04
    """
    # TODO: 임시 - DB query 구현 필요
    return [
        {
            "id": 101,
            "meal_type": "lunch",
            "eaten_at": "2025-12-04T12:35:10.000Z",
            "image_urls": [
                "https://caloreat.s3.ap-northeast-2.amazonaws.com/images/lunch_101.jpg"
                "https://caloreat.s3.ap-northeast-2.amazonaws.com/images/dinner_101.jpg"
            ],
            "created_at": "2025-12-04T12:40:00.000Z",
            "meal_items": [
                {
                    "id": 1,
                    "meal_log_id": 101,
                    "foodname": "된장찌개",
                    "quantity": 1,
                    "nutritions": {"calories": 230, "carbs": 18},
                },
                {
                    "id": 2,
                    "meal_log_id": 101,
                    "foodname": "김치",
                    "quantity": 1,
                    "nutritions": {"calories": 90, "carbs": 7},
                },
            ],
        }
        # image 아이디 필요
    ]


# update patch -> put변경  TODO: front 데이터수정 전송방식 meal부분 변경전달필요
@router.put("/log/{meal_id}")
async def update_meal_log_endpoint(
    foods: list[str],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    update_meal_log_endpoint

    :param foods: ["foodname1","foodname2",...]
    :type foods: list[str]

    """
    # TODO: 임시 - DB update 구현 필요
    return {"message": "updated"}


# delete / params: none
@router.delete("/log/{meal_id}")
async def delete_meal_log_endpoint(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # TODO: 임시 - DB 삭제 구현 필요
    return {"message": "deleted"}
