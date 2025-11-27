from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, Annotated
from enum import Enum

# user_allergies


# base
class AllergyBase(BaseModel):
    allergies: list[str]

    # allergy는 건강유의사항과 속성이다름 ->

    # severity: str | None = None


# request client가 보내는 필드
# allergies은 optional 필수 생성필드가 아니므로 create의 의미가 x


# create
class AllergyCreate(BaseModel):
    allergies: list[str] | None = None


# update
class AllergyUpdate(AllergyCreate):
    pass


# response
# read
class AllergyInDB(AllergyBase):
    id: int  # TODO: alias 적용 condition_id

    # created_at: datetime  # 기간별 상태변화 추적
    # updated_at:

    class Config:
        from_attributes = True


class AllergyRead(AllergyInDB):
    pass
