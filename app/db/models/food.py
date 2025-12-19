from sqlalchemy import Column, Integer, String, Float
from app.db.database import Base


class Food(Base):
    __tablename__ = "foods"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)


## TODO: food_db 연결 후 삭제
