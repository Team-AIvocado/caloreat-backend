from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional

# Meal Images


# base
class MealImageBase(BaseModel):
    image_url: str


# Image Response
class MealImageResponse(BaseModel):
    image_url: str
    food_name: str  # TODO: 모델반환필드 확인필요
    candidates: list[str] = Field(default_factory=list)


# Analized Response


# meal_log 사용
# class MealImageInDB(MealImageBase):
#     image_id: int = Field(..., alias="id")
#     created_at: Optional[datetime]

#     class Config:
#         from_attributes = True
#         populate_by_name = True
