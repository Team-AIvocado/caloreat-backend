from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, cast, String
from sqlalchemy.orm import selectinload
from app.db.database import get_db
from app.db.models.prediction_log import PredictionLog
from app.db.models.meal_log import MealLog
from app.db.models.meal_item import MealItem

router = APIRouter(prefix="/logs", tags=["Logs"])


@router.get("/predictions")
async def read_prediction_logs(limit: int = 10, db: AsyncSession = Depends(get_db)):
    """
    최근 적재된 예측 로그 조회
    (AWS IAM 권한 문제로 DB 직접 접근이 어려울 때 확인용)
    """
    stmt = select(PredictionLog).order_by(desc(PredictionLog.created_at)).limit(limit)
    result = await db.execute(stmt)
    logs = result.scalars().all()
    return logs


@router.get("/analysis")
async def analyze_prediction_accuracy(
    limit: int = 10, db: AsyncSession = Depends(get_db)
):
    """
    AI 예측 vs 사용자 실제 선택 함께 출력하는 엔드포인트
    PredictionLog와 MealLog를 image_id로 조인(유사)하여 비교 데이터를 반환 -> 백엔드에서 직접 or MLOps에서 원하는 결과 쉽게 확인
    """
    # 1. 최근 Prediction Log 조회
    stmt = select(PredictionLog).order_by(desc(PredictionLog.created_at)).limit(limit)
    result = await db.execute(stmt)
    pred_logs = result.scalars().all()

    analysis_data = []

    # 2. 각 로그에 대해 매칭되는 MealLog 검색 (N+1 문제 허용: Admin용이므로)
    for log in pred_logs:
        # MealLog.image_urls는 JSON 배열이지만, 텍스트로 캐스팅하여 image_id 포함 여부 검색
        # 예: image_urls=["s3://.../meals/{uuid}.jpg"] -> LIKE '%{uuid}%'
        meal_stmt = (
            select(MealLog)
            .options(selectinload(MealLog.meal_items))  # Item 정보 함께 로드
            .where(cast(MealLog.image_urls, String).like(f"%{log.image_id}%"))
        )
        meal_result = await db.execute(meal_stmt)
        matched_meal = meal_result.scalars().first()

        entry = {"prediction": log, "user_meal": None}

        if matched_meal:
            entry["user_meal"] = {
                "meal_id": matched_meal.id,
                "eaten_at": matched_meal.eaten_at,
                "items": [
                    {"foodname": item.foodname, "quantity": item.quantity}
                    for item in matched_meal.meal_items
                ],
            }

        analysis_data.append(entry)

    return analysis_data
