from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class Nutrition(Base):
    __tablename__ = "nutritions"

    id = Column(Integer, primary_key=True, index=True)
    food_id = Column(Integer, ForeignKey("foods.id"), nullable=False)

    # AI Client 응답 기준 최소 필드 (탄단지+칼로리)
    calories = Column(Float, nullable=True)  # kcal
    carbohydrate = Column(Float, nullable=True)  # g
    protein = Column(Float, nullable=True)  # g
    fat = Column(Float, nullable=True)  # g

    # Back Reference
    food = relationship("Food", back_populates="nutrition")
