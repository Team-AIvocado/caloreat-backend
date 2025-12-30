from pydantic import BaseModel, ConfigDict

# request pydantic 추가필요


# --response--


class FoodRead(BaseModel):
    id: int
    foodname: str

    model_config = ConfigDict(from_attributes=True)
