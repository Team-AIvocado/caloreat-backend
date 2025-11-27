from sqlalchemy import Column, BigInteger, String, ForeignKeyConstraint, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base


# 건강 및 식이 제한정보 user_health_conditions
# 현재 구현 편의성+ MVP 특성을위해 User:Allergy = 1:1
# TODO: AI모델쪽 파이프라인 들어올 시 1:N으로변경 + 비지니스로직 변경필요 (학습+영양소or식단log 축적)
class Allergy(Base):
    __tablename__ = "user_allergies"
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, unique=True)

    # 최소기능 속도위주 JSON형태 list형태로 저장
    allergies = Column(JSON, nullable=True)

    users = relationship("User", back_populates="user_allergies")

    __table_args__ = (
        ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )

    # allergies = Column(String(100), nullable=True) # TODO: AI model 연결시 list -> str + allergy_id 로 저장
    # severity = Column(String(10), nullable=True)  # low/ medium / high
