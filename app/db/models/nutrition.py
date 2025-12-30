from sqlalchemy import Column, Integer, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base


# rawdata warehouse
# 영양소 데이터를 저장하는 테이블
# 모델 영양소별 추론 정확도 평가 지표용 rawdata 저장용 (정답학습/비정답학습 모두 사용가능)
class Nutrition(Base):
    __tablename__ = "nutritions"

    id = Column(Integer, primary_key=True, index=True)
    food_id = Column(Integer, ForeignKey("foods.id"), nullable=False)

    # LLM Output 1:1 Mapping
    calories = Column(Float, nullable=True)
    carbs_g = Column(Float, nullable=True)
    protein_g = Column(Float, nullable=True)
    fat_g = Column(Float, nullable=True)
    sugar_g = Column(Float, nullable=True)
    fiber_g = Column(Float, nullable=True)
    sodium_mg = Column(Float, nullable=True)
    cholesterol_mg = Column(Float, nullable=True)
    saturated_fat_g = Column(Float, nullable=True)

    # micronutrients는 JSON 형태로 저장
    micronutrients = Column(JSON, nullable=True)

    # Back Reference
    food = relationship("Food", back_populates="nutrition")
