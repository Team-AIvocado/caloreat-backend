"""
영양 조언 관련 스키마

"""

from pydantic import BaseModel, Field
from typing import Optional


class TargetNutrition(BaseModel):
    """목표 영양소"""

    calorie: float = Field(..., description="목표 칼로리 (kcal)")
    carb: float = Field(..., description="목표 탄수화물 (g)")
    protein: float = Field(..., description="목표 단백질 (g)")
    fat: float = Field(..., description="목표 지방 (g)")


class CurrentIntake(BaseModel):
    """현재 섭취량"""

    calorie: float = Field(0, description="섭취 칼로리 (kcal)")
    carb: float = Field(0, description="섭취 탄수화물 (g)")
    protein: float = Field(0, description="섭취 단백질 (g)")
    fat: float = Field(0, description="섭취 지방 (g)")
    sodium: float = Field(0, description="섭취 나트륨 (mg)")


class NutritionAdviceResponse(BaseModel):
    """
    영양 조언 응답

    Example:
        {
            "target": {
                "calorie": 2055.5,
                "carb": 256.9,
                "protein": 128.5,
                "fat": 57.1
            },
            "current": {
                "calorie": 2500,
                "carb": 350,
                "protein": 80,
                "fat": 65,
                "sodium": 2500
            },
            "warnings": [
                "GOAL_CALORIE_OVER",
                "DIABETES_CARB_OVER"
            ]
        }
    """

    target: TargetNutrition = Field(..., description="목표 영양소")
    current: CurrentIntake = Field(..., description="현재 섭취량")
    warnings: list[str] = Field(default_factory=list, description="경고 코드 리스트")


class TargetOnlyResponse(BaseModel):
    """목표 영양소만 반환 (현재 섭취량 없이)"""

    target: TargetNutrition = Field(..., description="목표 영양소")


# 경고 코드 설명 (프론트엔드 참조용)
WARNING_MESSAGES = {
    # Goal 기반 경고
    "GOAL_CALORIE_OVER": "목표 칼로리를 초과했습니다.",
    "GOAL_CALORIE_UNDER": "목표 칼로리에 미달했습니다.",
    # Condition 기반 경고
    "DIABETES_CARB_OVER": "당뇨: 탄수화물 섭취 비율이 55%를 초과했습니다.",
    "HYPERTENSION_SODIUM_OVER": "고혈압: 나트륨 섭취량이 2000mg을 초과했습니다.",
    "HYPOTENSION_LOW_INTAKE": "저혈압: 칼로리 섭취가 목표의 70% 미만입니다.",
    "HYPERLIPIDEMIA_FAT_OVER": "고지혈증: 지방 섭취량이 70g을 초과했습니다.",
}
