from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from app.core.auth import get_current_user
from app.db.database import get_db
from app.db.models.user import User
from app.db.crud.meal_log import MealLogCrud
from app.db.schemas.nutrition_advice import (
    NutritionAdviceResponse,
    TargetOnlyResponse,
    TargetNutrition,
    CurrentIntake,
)
from app.services.nutrition_calculator import NutritionCalculatorService

router = APIRouter(prefix="/nutrition", tags=["Nutrition"])


def calculate_today_intake(meal_logs: list) -> dict:
    """
    오늘의 meal_logs에서 총 섭취량 계산

    Args:
        meal_logs: MealLog 객체 리스트 (meal_items 포함)

    Returns:
        {"calorie": float, "carb": float, "protein": float, "fat": float, "sodium": float}
    """
    total = {"calorie": 0.0, "carb": 0.0, "protein": 0.0, "fat": 0.0, "sodium": 0.0}

    for meal_log in meal_logs:
        for item in meal_log.meal_items:
            if item.nutritions:
                # nutritions JSON 구조에서 값 추출
                # AI 응답 형식: {"calories": N, "carbs_g": N, "protein_g": N, "fat_g": N, "sodium_mg": N}
                nutritions = item.nutritions
                quantity = item.quantity if item.quantity else 1.0

                total["calorie"] += (nutritions.get("calories", 0) or 0) * quantity
                total["carb"] += (nutritions.get("carbs_g", 0) or 0) * quantity
                total["protein"] += (nutritions.get("protein_g", 0) or 0) * quantity
                total["fat"] += (nutritions.get("fat_g", 0) or 0) * quantity
                total["sodium"] += (nutritions.get("sodium_mg", 0) or 0) * quantity

    # 소수점 1자리로 반올림
    return {k: round(v, 1) for k, v in total.items()}


@router.get("/target", response_model=TargetOnlyResponse)
async def get_target_nutrition(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    사용자의 목표 영양소 조회

    - BMR, TDEE 기반 계산
    - Goal (loss/maintain/gain)에 따른 칼로리 조정
    """
    target = await NutritionCalculatorService.get_user_target(db, current_user.id)
    return {"target": TargetNutrition(**target)}


@router.get("/advice", response_model=NutritionAdviceResponse)
async def get_nutrition_advice(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    오늘의 영양 조언 조회

    - 목표 영양소 (target)
    - 현재 섭취량 (current) - 오늘 기록된 meal_logs 기반
    - 경고 (warnings) - Goal 및 Condition 기반

    경고 코드:
    - GOAL_CALORIE_OVER: 목표 칼로리 초과
    - GOAL_CALORIE_UNDER: 목표 칼로리 미달
    - DIABETES_CARB_OVER: 당뇨 - 탄수화물 55% 초과
    - HYPERTENSION_SODIUM_OVER: 고혈압 - 나트륨 2000mg 초과
    - HYPOTENSION_LOW_INTAKE: 저혈압 - 칼로리 70% 미만
    - HYPERLIPIDEMIA_FAT_OVER: 고지혈증 - 지방 70g 초과
    """
    today = date.today()

    # 오늘의 meal_logs 조회
    meal_logs = await MealLogCrud.get_meal_logs_db(db, current_user.id, today)

    # 오늘 섭취량 계산
    current_intake = calculate_today_intake(meal_logs)

    # 목표 영양소 및 경고 생성
    result = await NutritionCalculatorService.get_nutrition_advice(
        db=db, user_id=current_user.id, current_intake=current_intake
    )

    return NutritionAdviceResponse(
        target=TargetNutrition(**result["target"]),
        current=CurrentIntake(**result["current"]),
        warnings=result["warnings"],
    )
