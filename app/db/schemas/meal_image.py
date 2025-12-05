from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional

# Meal Images


# base
# class MealImageBase(BaseModel):
#     image_url: str
# formdata uploadfile이므로


# Image Response
class MealImageResponse(BaseModel):
    image_id: str  # uuid : front 상태 식별용
    # image_url: str  # S3 url
    food_name: str  # TODO: 모델반환필드 확인필요
    candidates: list[dict] = Field(default_factory=list)


class OverrideResponse(BaseModel):
    image_id: str  # uuid : front 상태 식별용
    # image_url: str  # S3 url
    food_name: str  # TODO: 모델반환필드 확인필요
    candidates: list[dict] = Field(default_factory=list)
    corrected: bool = False


# Analized Response


# meal_log 사용
# class MealImageInDB(MealImageBase):
#     image_id: int = Field(..., alias="id")
#     created_at: Optional[datetime]

#     class Config:
#         from_attributes = True
#         populate_by_name = True
