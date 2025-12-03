from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional

# Meal Images


# Image Response
class MealImageResponse(BaseModel):
    image_id: str  # uuid : front 상태 식별용
    image_url: str  # S3 url
    food_name: str  # TODO: 모델반환필드 확인필요
    candidates: list[str] = Field(default_factory=list)
