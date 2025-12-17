from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional

# Nutrition, analysis
# 정규화고려 일단 다 나눔


# base


#     image_url: str
# -- request --
class AnalysisItem(BaseModel):
    image_id: str
    foodname: str


class MultiAnalysisRequest(BaseModel):
    foodnames: list[str]


class SingleAnalysisRequest(BaseModel):
    foodname: str  # 단일 음식 분석용 (문자열)


# Image Response
# 우선 분석결과 JSON 통으로 저장함 나중에 분리할거임
# 정규화 안함
# 테이블 id는 저장 전
#


# ===================================================
# LLM Response Schemas (Internal Use)
# ===================================================


class Micronutrients(BaseModel):
    # Common ones
    vitamin_c_mg: Optional[float] = None
    calcium_mg: Optional[float] = None
    caffeine_mg: Optional[float] = None
    # Allow extra fields for forward compatibility with LLM
    model_config = ConfigDict(extra="allow")


class NutritionDetail(BaseModel):
    calories: float
    carbs_g: float
    protein_g: float
    fat_g: float
    sugar_g: float
    fiber_g: float
    sodium_mg: float
    cholesterol_mg: float
    saturated_fat_g: float
    micronutrients: Micronutrients = Field(default_factory=Micronutrients)


# Image Response
class AnalysisResult(BaseModel):
    foodname: str
    nutritions: dict


class MultiAnalysisResponse(BaseModel):
    results: list[AnalysisResult]  # orm JSON # TODO: 정규화? 그런거모름 나중에함
    # -> 안하는이유 리스트로 받아서 찢어서 나누고


# Single Response
class SingleAnalysisResponse(AnalysisResult):
    pass


# ====================================


# meal.py 로 이전필요
### override 수정
class OverrideRequest(BaseModel):
    inference_id: str  # tmp 백엔드내 uuid부여 : front 다중음식 상태 식별용
    selected_food: str


class OverrideResponse(BaseModel):
    inference_id: str
    selected_food: str
    status: str = "updated"


# -----------------------------------
# textoverrride
class OverrideTextRequest(BaseModel):
    selected_food: str  # 수정할 foodname


class OverrideTextResponse(BaseModel):
    foodname: str
