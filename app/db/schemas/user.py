from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

# dabin
# 유지보수 + 기능추가확장성을위해 결합도를 최대한 낮추고 최소기능으로 구현


# 기본 유저 정보 스키마
class UserBase(BaseModel):
    email: EmailStr
    username: str


### Request schema
# 회원 가입용 스키마
class UserCreate(UserBase):
    password: str


# 회원 정보 수정용 스키마
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = (
        None  # 이메일 선택입력 -> None이면 변경하지 않음 -> 수정 시 필수 아님
    )
    username: Optional[str] = (
        None  # 유저이름 선택입력 -> None이면 변경하지 않음 -> 부분수정 대비
    )
    password: Optional[str] = None
    # phone삭제
    # 확장
    # provider : Optional[str] = None        # 가입경로 선택입력 -> 기본값 이미 DB에 있음
    # is_activate : Optional[bool] = None    # 활성화 여부 선택입력 -> None이면 미변경 상태 -> 수정만 허용
    # email_verified : Optional[bool] = None # 이메일 인증 여부 선택입력 -> None이면 미변경 상태 -> 시스템에서 변경할 값


# Response schema
# -> 결합도가 높음 : front_ui, db테이블구조, 기능으로  응답스키마를 3개로 분리


# 회원가입 (User)
class UserInDB(UserBase):
    id: int  # = Field(..., alias="id")          # 유저의 고유 ID(PK), 유저 식별용으로 필수 -> API 응답 전용 이름 user_id로변환
    created_at: datetime  # = Field(default_factory=lambda : datetime.now(timezone.utc))  #db읽어서 클라이언트 반환
    # provider : str                      # 유저의 가입경로, 로그인 방식 구분용 social 로그인 구현후 활성화

    class Config:
        from_attributes = True  # SQLAlchemy 모델을 바로 응답 모델로 변환 가능
        # Pydantic v2: from_attributes, v1이면 orm_mode = True


class UserRead(UserInDB):
    pass


# ===============================================================
# Profile
class UserProfile:
    pass


# user_health_condition (allergic, diabetes .. )
# HealthCondition
class UserCondition:
    pass


##### UserProfile / HealthCondition
# nickname : Optional[str] = None        # 닉네임 선택입력 -> Null허용
# nickname : Optional[str]            # 유저의 닉네임, 서비스에서 별칭을 따로 줄 수 있다면 사용
# phone : Optional[str]               # 유저의 전화번호, 선택적으로 제공하지 않아도 됨
# is_active : bool                    # 유저의 계정 활성 여부, True=정상, False=정지
# email_verified : bool               # 유저의 이메일 인증 여부, True=인증완료, False=인증실패
# login_fail_count : int              # 유저의 로그인 실패 횟수, locked_until 설정하는데 쓰임
# locked_until : Optional[datetime]   # 유저의 계정 잠금 해제 시간, 로그인 실패 횟수 초과 시 일시적으로 잠금
