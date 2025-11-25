from app.db.database import Base
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Annotated

# 건강 및 식이 제한정보 user_health_conditions
# 질병정보등은 선택사항
# 유저정보


# base
class HealthConditionBase(BaseModel):
    condition_name: str | None = None
    condition_type: str | None = None
    severity: str | None = None


# request
# create
class HealthConditionCreate(HealthConditionBase):
    pass


# update
class HealthConditionUpdate(HealthConditionBase):
    pass


# response
# read
class HealthConditionInDB(HealthConditionBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


class HealthConditionRead(HealthConditionInDB):
    pass
