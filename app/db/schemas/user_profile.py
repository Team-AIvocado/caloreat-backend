from app.db.database import Base
from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, Annotated

# entity: user_info(profile)
# 유저 : 프로필 = 1: 1 구조 user_id x -> 다른사람 프로필수정 공격 가능


# request schema
# UserProfile or UserInfo
class UserProfileBase(BaseModel):
    # nickname: str
    gender: str
    height: float | None = None
    weight: float | None = None
    birthdate: date | None = None  # immutable
    goal_type: str | None = None  # 미정 (직접입력, select선택)


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileUpdate(BaseModel):
    # nickname: str | None = None
    gender: str | None = None
    height: float | None = None
    weight: float | None = None
    goal_type: str | None = None


# response schema
class UserProfileInDB(UserProfileBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserProfileRead(UserProfileInDB):
    age: int | None = None  # 날짜가지남에따라 나이갱신이안됨 =계산후 주입필요
    # bmi: float |None = None # 몸무게, 키는 mutable 계산후 반환필요 - 우선 최소기능만
