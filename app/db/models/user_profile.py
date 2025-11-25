# 신체정보
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKeyConstraint,
    Float,
    BigInteger,
    Date,
    DateTime,
)
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime, timezone


# UserProfile or UserInfo
# user: profile = 1:1
class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(BigInteger, primary_key=True)  # SERIAL
    user_id = Column(BigInteger, unique=True)

    # nickname = Column(String(50), nullable=True)
    gender = Column(String(10), nullable=False)
    birthdate = Column(Date, nullable=False)  # Date객체 변경
    height = Column(Float, nullable=True)  # postgres DOUBLE PRECISION
    weight = Column(Float, nullable=True)
    goal_type = Column(String(100), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    # meal_pattern = Column(String(100), nullable=True) # 식습관패턴

    users = relationship("User", back_populates="user_profiles")

    __table_args__ = (
        ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
