from app.db.database import Base
from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, Annotated
from enum import Enum

# entity: user_info(profile)
# 유저 : 프로필 = 1: 1 구조 user_id x -> 다른사람 프로필수정 공격 가능


# --- request schema ---


# 달성목표 enum 처리
class GoalType(str, Enum):
    loss = "loss"
    maintain = "maintain"
    gain = "gain"
    # TODO: healthcare 추가여부


# UserProfile(UserInfo)
class UserProfileBase(BaseModel):
    # nickname: str
    gender: str  #  male ,  female
    birthdate: date | None = None  # immutable / age = mutable
    height: float | None = None
    weight: float | None = None
    goal_type: GoalType | None = None  # 미정 (직접입력, select선택)


class UserProfileCreate(UserProfileBase):
    user_id: int


class UserProfileUpdate(BaseModel):
    # nickname: str | None = None
    # gender: str | None = None # TODO: 성별은 수정하면안됨?(성전환고려?...)
    height: float | None = None
    weight: float | None = None
    goal_type: str | None = None


# --- response schema ---
class UserProfileInDB(UserProfileBase):
    profile_id: int = Field(..., alias="id")
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserProfileRead(UserProfileInDB):
    age: int | None = None  # 날짜가지남에따라 나이갱신이안됨 =계산후 주입필요
    # bmi: float |None = None # 몸무게, 키는 mutable 계산후 반환필요 - 우선 최소기능만
