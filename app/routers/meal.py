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
    MultiAnalysisResponse,
    MultiAnalysisRequest,
    SingleAnalysisRequest,
    SingleAnalysisResponse,
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


# --- back client - llm server ---
# 음식 text 영양소분석
# 1단계 image detect/cls 에서 선택된 이미지 (아/점/저)
# 사용자확인 전단계가 존재하므로 confidence는 생략 foodname만 전달


# 한끼(점심)에 먹는 음식(str)이 여러개임
# inferserver request는 하나씩 낱개로
# # TODO: DB 검색 & 없는경우 LLM Module 호출 -> ai-server로 책임이관


@router.post("/analyze/single", response_model=SingleAnalysisResponse)
async def analyze_single_nutrition_endpoint(request: SingleAnalysisRequest):
    # Service Skeleton 호출 (Single)
    return await MealItemService.one_food_analysis(request.foodname)


# # 복수요청 # TODO: 음식 복수선택시 llm module 복수 분석 router필요
# @router.post("/analyze", response_model=MultiAnalysisResponse)
# async def analyze_nutrition_endpoint(request: MultiAnalysisRequest):
#     # Service Skeleton 호출 (List)
#     return await MealItemService.food_analysis(request.foodnames)
# return {
#     "results": [
#         {"foodname": "된장찌개", "nutritions": {"calories": 230, "carbs": 18}},
#         {"foodname": "김치", "nutritions": {"calories": 90, "carbs": 7}},
#     ]
# }  # nutiritionsta


# ===================================================

# output & meal_log, item crud


# -- meal_log crud --
# image s3업로드, tmp 삭제, db저장 라우터
@router.post("/log", response_model=MealLogRead)
async def create_meal_log_endpoint(
    meal: MealLogCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    create_meal_log_endpoint
    meal_type: breakfast, launch, dinner, snack(opt.)
    """
    # Service호출
    return await MealLogService.create_meal_log(db, current_user.id, meal)


# read by date/ query
# 날짜별 식단조회 아침,점심,저녁
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
    user_id = current_user.id
    return await MealLogService.read_meal_log(db, user_id, date)


# update patch -> put변경  TODO: front 데이터수정 전송방식 meal부분 변경전달필요
# update (PUT)
@router.put("/log/{meal_id}", response_model=MealLogRead)
async def update_meal_log_endpoint(
    meal_id: int,
    meal_update: MealLogUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    식단 수정 API (Full Replace)
    - 본인이 작성한 식단만 수정 가능
    - 요청 본문의 내용으로 식단을 통째로 교체
    - 메타데이터(시간, 타입) 업데이트 (이미지 수정 불가)
    - 음식 목록 전체 교체 (기존 삭제 -> 신규 생성)
    """
    return await MealLogService.update_meal_log(
        db, current_user.id, meal_id, meal_update
    )


# delete / params: none
@router.delete("/log/{meal_id}")
async def delete_meal_log_endpoint(
    meal_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> bool:
    """
    삭제 시 MealItem 자동 삭제 (ON DELETE CASCADE)
    """
    return await MealLogService.delete_meal_log(db, current_user.id, meal_id)  # boolean
