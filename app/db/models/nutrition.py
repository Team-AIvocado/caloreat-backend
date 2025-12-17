from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Float,
    JSON,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from app.db.database import Base


class Nutrition(Base):
    """
    영양소 상세 테이블 (Nutrition Detail)
    - 역할: Food의 표준 영양 정보 (1인분, 100g 등 기준값)
    - 구조: 하이브리드 (주요 영양소는 컬럼, 미량 영양소는 JSON)
    """

    __tablename__ = "nutritions"

    id = Column(BigInteger, primary_key=True)
    food_id = Column(
        BigInteger,
        ForeignKey("foods.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    # 데이터 출처 (예: LLM, USER, ADMIN, USDA)
    source = Column(String(50), default="LLM", nullable=False)

    # --- 주요 영양소 (정규화) ---
    calories = Column(Float, nullable=False, default=0.0)
    carbs_g = Column(Float, nullable=False, default=0.0)
    protein_g = Column(Float, nullable=False, default=0.0)
    fat_g = Column(Float, nullable=False, default=0.0)

    # --- 상세 영양소 (반정규화/선택적 정규화) ---
    # 자주 쓰이거나 필터링에 필요한 항목들
    sugar_g = Column(Float, nullable=True, default=0.0)
    fiber_g = Column(Float, nullable=True, default=0.0)
    sodium_mg = Column(Float, nullable=True, default=0.0)
    cholesterol_mg = Column(Float, nullable=True, default=0.0)
    saturated_fat_g = Column(Float, nullable=True, default=0.0)

    # --- 미량 영양소 및 기타 (JSON) ---
    # vitamin_c, calcium, caffeine 등 확장성 있는 데이터
    micronutrients = Column(JSON, nullable=True, default={})

    food = relationship("Food", back_populates="nutrition")
