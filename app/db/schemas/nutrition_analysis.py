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


# Image Response
# 우선 분석결과 JSON 통으로 저장함 나중에 분리할거임
# 정규화 안함
# 테이블 id는 저장 전
#
class NutrientAnalysisResponse(BaseModel):
    foodname: str
    nutrition: dict  # orm JSON


# ====================================


# meal.py 로 이전필요
#### override 수정
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
