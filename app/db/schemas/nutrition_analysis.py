from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional

# Nutrition, analysis
# 정규화고려 일단 다 나눔


# base
# class MealImageBase(BaseModel):
#     image_url: str
# -- request --
class AnalysisRequest(BaseModel):
    foodnames: list[str]  # kakao pasta 최대칼로리 넘으면 음식추가안됨?
    # 아침 점심 저녁 나눌거면 list[dict]  {meal_type:1(아침), foodname: "김치찌개"}

# Image Response
# 우선 분석결과 JSON 통으로 저장함 나중에 분리할거임
# 정규화 안함
# 테이블 id는 저장 전
#

class AnalysisResult(BaseModel):
    foodname: str
    nutritions: dict

class NutrientAnalysisResponse(BaseModel):
    results: list[AnalysisResult]  # orm JSON # TODO: 정규화? 그런거모름 나중에함
    # -> 안하는이유 리스트로 받아서 찢어서 나누고 


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
