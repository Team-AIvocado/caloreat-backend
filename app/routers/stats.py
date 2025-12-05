from fastapi import APIRouter, Depends, status, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_user_id, get_current_user
from app.db.models import User
from app.db.database import get_db
from app.db.schemas.stats import (
    TodaySummary,
    HourNutrition,
    DayStatsResponse,
    MonthStatsResponse,
)
from datetime import date
from calendar import month

# Stats
# 읽기전용 계산 도메인

dashboard_router = APIRouter(prefix="/dashboard", tags=["DashBoard"])
stats_router = APIRouter(prefix="/stats", tags=["Stats"])


# dashboard
@dashboard_router.get("/today", response_model=TodaySummary)
async def get_today_summary_endpoint(
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    pass
    # return { "total_kcal": 1200, "carbo": 150 }
    # return await StatsService.get_today_summary(db, user_id)


# stats
# 일간
@stats_router.get("/day", response_model=DayStatsResponse)
async def get_day_stats_endpoint(
    date: date,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    pass


#     return { "breakfast": 300, "lunch": 500}

# TODO: 시간별 추가여부


# 주간
@stats_router.get("/week")
async def get_month_stats_endpoint(
    start_date: date,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    pass
    # return {"dates": ["01", "02"], "kcal": [30, 20]}


# 월간
@stats_router.get("/month", response_model=MonthStatsResponse)
async def get_month_stats_endpoint(
    month: int,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    pass
    # return { "avg_kcal": 1800, "total_days": 30 }
