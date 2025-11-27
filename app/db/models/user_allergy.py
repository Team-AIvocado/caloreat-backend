from sqlalchemy import Column, BigInteger, String, ForeignKeyConstraint, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base


# 건강 및 식이 제한정보 user_health_conditions
class Allergy(Base):
    __tablename__ = "user_allergies"
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, unique=True)

    # 최소기능 속도위주 JSON형태 list형태로 저장
    allergies = Column(JSON, nullable=True)
    # allergies = Column(String(100), nullable=True) # TODO: AI model 연결시 활성화
    # condition_type = Column(String(50), nullable=True)  # disease, allergy, ..
    # severity = Column(String(10), nullable=True)  # low/ medium / high

    users = relationship("User", back_populates="user_allregies")

    __table_args__ = (
        ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )

    # activity_level = Column(Integer, nullable=True) # 운동량(하루활동량)
