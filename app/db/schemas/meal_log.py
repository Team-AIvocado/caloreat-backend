from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


# MealItems (끼니별 음식 항목)

# ---request ---
# calorie, nutrition은 llm반환값그대로 스냅샷(JSON)형태로 통저장


# base
class MealItemBase(BaseModel):
    foodname: str
    quantity: float  # TODO: 음식별 섭취량(1개or g정량단위) 확정필요
    nutritions: dict  # calorie+ nutrition

    # calorie: float
    # llm응답에 포함되어오는지 백에서 계산해야하는지 알수없음(탄,단,단지->calorie)


# create
class MealItemCreate(MealItemBase):
    pass


# --- response ---
# read
class MealItemInDB(MealItemBase):
    meal_item_id: int = Field(..., alias="id")
    meal_log_id: int  # FK (JSON에 존재함)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)  # 예외발생 안전장치 추가


class MealItemRead(MealItemInDB):
    pass


# ===============================================


# MealLog (식단기록헤더) : 1:N 구조에서 부모테이블


# - base -
class MealLogBase(BaseModel):
    meal_type: str  # 아침/ 점심 /저녁
    eaten_at: datetime  # 식사시간 ≠ created_at : db저장시간


# -- request --
class MealLogCreate(MealLogBase):
    """
    아침, 점심, 저녁 음식리스트 JSON 형태 통으로저장
    """

    meal_items: list[MealItemCreate]


class MealLogUpdate(MealLogBase):
    """
    PUT사용 -> 통으로 교체
    """

    meal_items: list[MealItemCreate]


# --- response ---
class MealLogInDB(MealLogBase):
    meal_log_id: int = Field(..., alias="id")  # PK
    image_urls: list[str]  # s3 image_url들은 아침,점심,저녁 테이블에
    created_at: datetime

    # user_id: int  body포함 x
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class MealLogRead(MealLogInDB):
    meal_items: list[MealItemRead]
