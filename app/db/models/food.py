from sqlalchemy import Column, Integer, String, Float
from app.db.database import Base
from sqlalchemy.orm import relationship


class Food(Base):
    __tablename__ = "foods"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)

    # 1:1 or 1:N (단순화를 위해 일단 list로 접근 가능하게 설정하되, 로직상 1:1 유지)
    nutrition = relationship(
        "Nutrition", back_populates="food", uselist=False, cascade="all, delete-orphan"
    )


## TODO: food_db 연결 후 삭제
