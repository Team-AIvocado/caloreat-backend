from sqlalchemy import Column, Integer, String, Float, DateTime
from app.db.database import Base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone


class Food(Base):
    __tablename__ = "foods"

    id = Column(Integer, primary_key=True, index=True)
    foodname = Column(String, unique=True, index=True, nullable=False)
    # 기본음식이름 저장 후 DB 조회(모델별 음식이름 구분용도)
    source = Column(String, nullable=False, default="llm")
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # 1:1 or 1:N (단순화를 위해 일단 list로 접근 가능하게 설정하되, 로직상 1:1 유지)
    nutrition = relationship(
        "Nutrition", back_populates="food", uselist=False, cascade="all, delete-orphan"
    )
