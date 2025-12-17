from sqlalchemy import (
    Column,
    BigInteger,
    String,
    DateTime,
)
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime, timezone


class Food(Base):
    """
    음식 마스터 테이블 (Master Data)
    - 역할: 영양소 정보의 기준이 되는 음식 엔티티
    - 특징: 이름(name)을 기준으로 식별 및 캐싱
    """

    __tablename__ = "foods"

    id = Column(BigInteger, primary_key=True)

    # 검색 및 캐싱의 핵심 키 (한글 이름)
    name = Column(String(100), unique=True, nullable=False, index=True)

    # 부가 정보
    name_en = Column(String(100), nullable=True)  # 영문명
    thumbnail_url = Column(
        String(500), nullable=True
    )  # 썸네일 (Optional) #TODO: S3 URL인데 리뷰필요
    description = Column(String(255), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # 1:1 관계 (Food -> Nutrition)
    nutrition = relationship(
        "Nutrition", back_populates="food", uselist=False, cascade="all, delete-orphan"
    )
