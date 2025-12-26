from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional

# dabin
# 유지보수 + 기능추가확장성을위해 결합도를 최대한 낮추고 최소기능으로 구현


# 기본 유저 정보 스키마
class UserBase(BaseModel):
    email: EmailStr
    username: str
    nickname: str | None = None  # 닉네임 선택입력 -> Null허용


### Request schema
# 회원 가입용 스키마
class UserCreate(UserBase):
    password: str


# 회원 정보 수정용 스키마
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None  # mutable?
    # username: Optional[str] = None  # immutable
    nickname: str | None = None
    phone: str | None = None
    is_active: bool | None = None
    email_verified: bool | None = None

    # provider: str = "local"       # 가입경로 선택입력 -> 기본값 이미 DB에 있음
    # is_activate : Optional[bool] = None    # 활성화 여부 선택입력 -> None이면 미변경 상태 -> 수정만 허용
    # email_verified : Optional[bool] = None # 이메일 인증 여부 선택입력 -> None이면 미변경 상태 -> 시스템에서 변경할 값
    # is_deleted: bool = False # TODO: soft delete


# front request body 검증용
class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str


# login
class UserLogin(BaseModel):
    account: str  # username or email이므로 emailstr금지 -> 무조건 str
    password: str


# -------------------------------------------

# Response schema
# -> 결합도가 높음 : front_ui, db테이블구조, 기능으로  응답스키마를 3개로 분리


# 회원가입 (User)
class UserInDB(UserBase):
    user_id: int = Field(
        ..., alias="id"
    )  # 유저의 고유 ID(PK), 유저 식별용으로 필수 -> API 응답 전용 이름 user_id로변환
    created_at: datetime  # = Field(default_factory=lambda : datetime.now(timezone.utc))  #db읽어서 클라이언트 반환
    # provider : str      # 유저의 가입경로, 로그인 방식 구분용 social 로그인 구현후 활성화

    model_config = ConfigDict(from_attributes=True)  # SQLAlchemy 모델을 바로 응답 모델로 변환 가능
    # Pydantic v2: from_attributes, v1이면 orm_mode = True

class UserRead(UserInDB):
    phone: str | None = None
    is_active: bool
    email_verified: bool | None = None
    provider: str = "local"  # 소셜 로그인 구분 (local, kakao, google)


class UserDetailRead(BaseModel):
    user_id: int = Field(..., alias="id")
    username: str
    email: str
    created_at: datetime


# 로그인 반환 (쿠키방식이라 토큰 필요 x)
class LoginResponse(UserRead):
    pass


class LogoutResponse(BaseModel):
    success: bool = True


# ===============================================================
# Profile
class UserProfile:
    pass


# user_health_condition (allergic, diabetes .. )
# HealthCondition
class UserCondition:
    pass


class MessageResponse(BaseModel):
    message: str


# # Optional
# is_active : bool                    # 유저의 계정 활성 여부, True=정상, False=정지
# email_verified : bool               # 유저의 이메일 인증 여부, True=인증완료, False=인증실패
# login_fail_count : int              # 유저의 로그인 실패 횟수, locked_until 설정하는데 쓰임
# locked_until : Optional[datetime]   # 유저의 계정 잠금 해제 시간, 로그인 실패 횟수 초과 시 일시적으로 잠금
