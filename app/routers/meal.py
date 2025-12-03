from fastapi import APIRouter, Depends, status, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_user_id, get_current_user
from app.db.models import User
from app.db.database import get_db

# 스키마
from app.db.schemas.meal_image import MealImageResponse
from app.db.schemas.nutrition_analysis import (
    NutrientAnalysisResponse,
    AnalysisRequest,
    OverrideRequest,
    OverrideResponse,
    OverrideTextResponse,
    OverrideTextRequest,
)

import io

# 서비스
from app.services.meal_image import MealImageService

# meal domain ux흐름 일치 엔드포인트끼리 묶음
# meal_log, meal_item, meal_image
# 이미지업로드 라우터에서 끝 /db저장 x (v1)

router = APIRouter(prefix="/meals/", tags=["MealImage"])


# 식단이미지 upload -> #TODO: (back-infer) request classification
@router.post("/upload", response_model=MealImageResponse)
async def upload_image_endpoint(
    # current_user: User = Depends(get_current_user),
    file: UploadFile = File(None),
):
    return {
        "image_url": "https://s3.../uuid.jpg",  # presigned URL
        "foodname": "된장찌개",  # response.candidates[0]["label"]
        "candidates": [
            {"label": "된장찌개", "confidence": 0.93},
            {"label": "김치찌개", "confidence": 0.72},
        ],
    }


# foodname = front state 값 db 저장x


# --- input ---
## meal_image Upload / meal_image.py집합


# 음식이름 수정 (선택된음식이름)
@router.post("/override/image", response_model=OverrideResponse)
async def override_prediction_endpoint(override_image: OverrideRequest):
    return OverrideResponse(
        inference_id=override_image.inference_id,
        selected_food=override_image.selected_food,
        status="updated",
    )


# 텍스트 입력(수동입력) /manual
@router.post("/override/text", response_model=OverrideTextResponse)
async def analyze_text(override_text: OverrideTextRequest):
    return OverrideTextResponse(foodname=override_text.selected_food)


# 음식 text 영양소분석
# 사용자확인 전단계가 존재하므로 confidence는 생략 foodname만 전달
# 한끼(점심)에 먹는 음식(str)이 여러개임
# inferserver request는 하나씩 낱개로
@router.post("/analyze", response_model=NutrientAnalysisResponse)
async def analyze_image_endpoint(foodnames: AnalysisRequest):

    return {
        "results": [
            {
                "foodname": "된장찌개",
                "nutrition": {
                    "calories": 230,
                    "carbs": 18,
                },
            },
            {
                "foodname": "김치",
                "nutrition": {
                    "calories": 90,
                    "carbs": 7,
                },
            },
        ]
    }


# ===================================================
# output & meal_log, item crud

# create
# read
# update
# delete
