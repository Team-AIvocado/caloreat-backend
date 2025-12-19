from pydantic import BaseModel, ConfigDict

# request pydantic 추가필요


# --response--
class FoodRead(BaseModel):
    id: int
    name: str


# TODO: food_db 연결 후 삭제
