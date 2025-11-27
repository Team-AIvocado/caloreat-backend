from sqlalchemy import Column, BigInteger, String, ForeignKeyConstraint, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base


# 건강 및 식이 제한정보 user_health_conditions
class HealthCondition(Base):
    __tablename__ = "user_health_conditions"
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, unique=True)

    conditions = Column(JSON, nullable=True)

    users = relationship("User", back_populates="user_health_conditions")

    __table_args__ = (
        ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )

    # condition = Column(String(100), nullable=True) # TODO: 이후 AI 연결후 정규화
    # condition_type = Column(String(50), nullable=True)  # disease, allergy, ..
    # severity = Column(String(10), nullable=True)  # low/ medium / high
    # activity_level = Column(Integer, nullable=True) # 운동량(하루활동량)
