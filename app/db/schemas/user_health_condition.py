from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, Annotated
from enum import Enum

# 건강 및 식이 제한정보 user_health_conditions
# 질병정보등은 선택사항
# 유저: condition = 1:n
# 향후 ai 학습or 추론 고려 개별 endpoints작성


# base
class HealthConditionBase(BaseModel):
    conditions: list[str] | None = None


# condition_type: str | None = None
# allergy는 건강유의사항과 속성이다름 -> ㅇ
# severity: str | None = None


# request client가 보내는 필드
# optional임


# create
class HealthConditionCreate(HealthConditionBase):
    pass


# update
class HealthConditionUpdate(HealthConditionCreate):
    pass


# response
# read
class HealthConditionInDB(HealthConditionBase):
    condition_id: int = Field(..., alias="id")  # alias 적용 condition_id

    # created_at: datetime  # 기간별 상태변화 추적필요하면 활성화
    pass
    # updated_at:

    class Config:
        from_attributes = True


class HealthConditionRead(HealthConditionInDB):
    pass
