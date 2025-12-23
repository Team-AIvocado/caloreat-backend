from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.db.models import User
from app.db.database import get_db
from app.db.schemas.stats import (
    StatsResponse,
    TodaySummary,
)
from datetime import date
from app.services.stats import StatsService

dashboard_router = APIRouter(prefix="/dashboard", tags=["DashBoard"])
stats_router = APIRouter(prefix="/stats", tags=["Stats"])


# dashboard
@dashboard_router.get("/today", response_model=TodaySummary)
async def get_today_summary_endpoint(
    date: date,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # TODO: Dashboard용 요약 정보 (필요시 StatsService에 추가 구현)
    return {"total_calorie": 0, "carb": 0, "protein": 0, "fat": 0}


# stats
# 일간 통계
@stats_router.get("/daily", response_model=StatsResponse)
async def get_daily_stats_endpoint(
    date: date,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    일간 영양 섭취 통계 조회
    """
    # StatsService를 통해 일간 데이터 계산 및 반환
    return await StatsService.get_daily_stats(db, current_user.id, date)


# 주간 통계
@stats_router.get("/weekly", response_model=StatsResponse)
async def get_weekly_stats_endpoint(
    startDate: date,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    주간 영양 섭취 통계 조회 (startDate부터 7일간)
    """
    # StatsService를 통해 주간 데이터(7일 평균) 계산 및 반환
    return await StatsService.get_weekly_stats(db, current_user.id, startDate)


# 월간 통계
@stats_router.get("/monthly", response_model=StatsResponse)
async def get_month_stats_endpoint(
    year: int,
    month: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    월간 영양 섭취 통계 조회
    """
    # StatsService를 통해 월간 데이터(월 평균) 계산 및 반환
    return await StatsService.get_monthly_stats(db, current_user.id, year, month)
