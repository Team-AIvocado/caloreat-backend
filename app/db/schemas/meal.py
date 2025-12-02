from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, Annotated
from enum import Enum

# meal


# Base
class MealImageBase(BaseModel):
    field1: str


# request
class MealImageCreate(BaseModel):
    field1: str
    field2: int | None = None


class MealImageUpdate(BaseModel):
    field1: str | None = None
    field2: int | None = None


# --- response ---
class MealImageInDB(MealImageBase):
    image_id: int = Field(..., alias="id")  # PK
    user_id: int  # FK가 있으면 유지
    created_at: datetime

    class Config:
        from_attributes = True


class MealImageRead(MealImageInDB):
    pass
