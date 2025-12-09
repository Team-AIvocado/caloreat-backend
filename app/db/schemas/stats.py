from pydantic import BaseModel, Field
from typing import List, Dict


# --response--
# ---------- 공통 구조 ----------
class Macro(BaseModel):
    calorie: float = 0.0
    carb: float = 0.0
    protein: float = 0.0
    fat: float = 0.0


# ---------- Dashboard Today ----------
class TodaySummary(BaseModel):
    total_calorie: float
    carb: float
    protein: float
    fat: float


# ---------- Day Stats ----------
class HourNutrition(BaseModel):
    hour: int = Field(..., description="0~23")
    calorie: float
    carb: float
    protein: float
    fat: float


class DayStatsResponse(BaseModel):
    date: str
    hourly: list[HourNutrition]  # 시간대별 섭취량
    total: Macro  # 하루 총합


# ---- Month Stats
class MonthStatsResponse(BaseModel):
    year: int
    month: int
    daily: list[Macro]  # 일별 집계
    total: Macro  # 월 총합
