from pydantic import BaseModel, Field
from typing import List, Dict, Optional


# -- response --
# ---------- 공통 구조 ----------
class NutrientDetail(BaseModel):
    amount: float = 0.0
    percentage: float = 0.0


class Nutrients(BaseModel):
    carbs: NutrientDetail = Field(default_factory=NutrientDetail)
    protein: NutrientDetail = Field(default_factory=NutrientDetail)
    fat: NutrientDetail = Field(default_factory=NutrientDetail)
    sugar: float = 0.0
    fiber: float = 0.0
    sodium: float = 0.0
    cholesterol: float = 0.0
    saturated_fat: float = 0.0


class Goals(BaseModel):
    sugar: float
    fiber: float
    sodium: float
    cholesterol: float
    saturated_fat: float


class ChartData(BaseModel):
    name: str
    calories: float
    goal: float


class DailyLogItem(BaseModel):
    id: int
    mealType: str
    timestamp: str
    name: str
    calories: float


# ---------- Stats Responses ----------
class StatsResponse(BaseModel):
    type: str
    date: str
    totalCalories: float
    nutrients: Nutrients
    goals: Optional[Goals] = None  
    chartData: List[ChartData] = []
    dailyLogs: List[DailyLogItem] = []
    showAlert: bool = True 


# ---------- Dashboard Today  ----------
class TodaySummary(BaseModel):
    total_calorie: float
    carb: float
    protein: float
    fat: float


# ---------- Day Stats  ----------
class HourNutrition(BaseModel):
    hour: int = Field(..., description="0~23")
    calorie: float
    carb: float
    protein: float
    fat: float


class DayStatsResponse(BaseModel):
    date: str
    hourly: list[HourNutrition]  # 시간대별 섭취량
    total: TodaySummary  # 하루 총합


# ---- Month Stats 
class MonthStatsResponse(BaseModel):
    year: int
    month: int
    daily: list[TodaySummary]  # 일별 집계
    total: TodaySummary  # 월 총합
