from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.database import get_db
from app.db.models.prediction_log import PredictionLog

router = APIRouter(prefix="/logs", tags=["Logs"])


@router.get("/recent")
async def read_prediction_logs(limit: int = 10, db: AsyncSession = Depends(get_db)):
    """
    백엔드에서 직접 최근 로그 확인용
    """
    stmt = select(PredictionLog).order_by(desc(PredictionLog.created_at)).limit(limit)
    result = await db.execute(stmt)
    logs = result.scalars().all()
    return logs
