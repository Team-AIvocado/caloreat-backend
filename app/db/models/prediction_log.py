from sqlalchemy import Column, BigInteger, String, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.database import Base
from datetime import datetime, timezone


class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    image_id = Column(
        String, unique=True, nullable=False, index=True
    )  # UUID string from frontend/service
    user_id = Column(BigInteger, nullable=False, index=True)
    raw_response = Column(JSON, nullable=False)
    model_version = Column(String(50), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
