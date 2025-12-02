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
# 테이블 id는
class NutrientAnalysisResponse(BaseModel):
    foodname: str
    nutrition: dict  # orm JSON
