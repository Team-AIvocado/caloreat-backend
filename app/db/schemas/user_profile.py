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


# UserProfile(UserInfo)
class UserProfileBase(BaseModel):
    gender: str  #  male ,  female
    birthdate: date | None = None  # immutable / age = mutable
    height: float | None = None
    weight: float | None = None
    goal_type: GoalType | None = None  # 미정 (직접입력, select선택)


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileUpdate(BaseModel):
    height: float | None = None
    weight: float | None = None
    goal_type: GoalType | None = None

    # gender: str | None = None # TODO: 성별은 수정하면안됨?(성전환고려?...)


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


# ------------------------------------------------------
# ProfileForm (condition, allergy 필드 추가 별도필드)
# ------------------------------------------------------


class ProfileFormBase(BaseModel):
    # nickname: str
    gender: str  #  male ,  female
    birthdate: date | None = None  # immutable / age = mutable
    height: float | None = None
    weight: float | None = None
    goal_type: GoalType | None = None  # 미정 (직접입력, select선택)


class ProfileFormCreate(ProfileFormBase):
    # user_id: int
    # 특수필드 추가(생성)
    conditions: list[str] | None = None


# request = response 동시사용
class ProfileFormUpdate(BaseModel):
    height: float | None = None
    weight: float | None = None
    goal_type: GoalType | None = None
    conditions: list[str] | None = None

    # gender: str | None = None # TODO: unrecognized


# --- response schema ---
class ProfileFormInDB(ProfileFormBase):
    # id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# create 전용 (age제거)
# alias는 InDB내 정의 x(상속시 alias import꼬임문제)
class ProfileFormResponse(ProfileFormInDB):
    conditions: list[str] = Field(default_factory=list)


class ProfileFormRead(ProfileFormInDB):
    age: int | None = None  # 날짜가지남에따라 나이갱신이안됨 =계산후 주입필요
    conditions: list[str] = Field(default_factory=list)

    # optional
    # profile_id: int = Field(..., alias="id") # front 요청시 활성화, conditions로직 수정도 필요
    # allergies: list[str] = Field(default_factory=list)
    # bmi: float |None = None # 몸무게, 키는 mutable 계산후 반환필요 - 우선 최소기능만
