from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, Annotated
from enum import Enum

# 건강 및 식이 제한정보 user_health_conditions
# 유저: condition = 1:n
# 향후 ai 학습or 추론 고려 개별 endpoints작성


# base
class HealthConditionBase(BaseModel):
    conditions: str


# --- request : optional ---


# create
class HealthConditionCreate(HealthConditionBase):
    pass


# update
class HealthConditionUpdate(HealthConditionBase):
    pass


# --- response ---
# read
class HealthConditionInDB(HealthConditionBase):
    condition_id: int = Field(..., alias="id")  # alias 적용 condition_id
    pass

    # created_at: datetime  # 기간별 상태변화 추적필요하면 활성화
    # updated_at:

    class Config:
        from_attributes = True


class HealthConditionRead(HealthConditionInDB):
    pass


#
