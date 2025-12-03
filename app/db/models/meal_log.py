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


class MealLog(Base):
    __tablename__ = "meal_logs"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, unique=False, nullable=False)
    meal_type = Column(String(30), nullable=False)
    eaten_at = Column(DateTime(timezone=True), nullable=False)  # 유저입력 datetime()
    image_urls = Column(JSON, nullable=True)  # JSON imgurl 통으로저장(식단에대한)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    user = relationship("User", back_populates="meal_logs")  # 1:N
    meal_items = relationship(
        "MealItem", back_populates="meal_logs", passive_deletes=True
    )
    # passive_deletes : FK cascade 우선사용

    __table_args__ = (
        ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )


# TODO: relationship logic 작성시 추가 (orm code 사용 예정)
