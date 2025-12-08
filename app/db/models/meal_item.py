from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Float,
    JSON,
    ForeignKey,
    DateTime,
    ForeignKeyConstraint,
)
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime, timezone


# MealItems : 하루에 먹은 식단(음식)


# meal_logs / meal_items  1: N
class MealItem(Base):
    __tablename__ = "meal_items"

    id = Column(BigInteger, primary_key=True)
    meal_log_id = Column(BigInteger, nullable=False)
    quantity = Column(Float, nullable=False)
    nutiritionsta = Column(JSON, nullable=True)  # 음식이름, 영양소정보 통저장
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    meal_logs = relationship("MealLog", back_populates="meal_items")

    __table_args__ = (
        ForeignKeyConstraint(["meal_log_id"], ["meal_logs.id"], ondelete="CASCADE"),
        # user_id 있으면 x 데이터 무결성 깨짐
    )


# 부모 (meallog)는 user_id를 알아야함 / 자식(meal_item)은 user_id를 몰라야함 - 주체기준판단
