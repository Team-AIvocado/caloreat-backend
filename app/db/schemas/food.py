from pydantic import BaseModel

# request pydantic 추가필요


# --response--


class FoodRead(BaseModel):
    id: int
    foodname: str

    class Config:
        from_attributes = True
