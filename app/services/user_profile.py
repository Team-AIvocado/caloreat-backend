from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.schemas.user_profile import (
    UserProfileCreate,
    UserProfileRead,
    UserProfileUpdate,
)
from app.db.models.user_profile import UserProfile
from app.db.crud.user_profile import UserProfileCrud

from enum import Enum
from datetime import date

# 신체정보
# TODO: 예외처리, null값 처리 -> 최소기능우선


# UserProfile(UserInfo)
class UserProfileService:

    # create(input form)                     #속성 -> 객체형태로 단순화(pydantic model:requestbody)
    @staticmethod
    async def create_profile(
        db: AsyncSession, user_id: int, profile: UserProfileCreate
    ):
        # commit / rollback transaction service에서개별관리
        # DB쓰기작업 transaction rollback 1차안전장치
        dict_profile = profile.model_dump()
        # user_id
        dict_profile["user_id"] = user_id

        # Enum:미리 정의된 값들의집합(상수타입)
        # 허용된값만 선택하도록 강제 : 서버관점, DB무결성, 프론트입력통제

        # Enum -> str(value) 변환(DB저장)
        goal_type = dict_profile.get("goal_type")
        if isinstance(goal_type, Enum):
            dict_profile["goal_type"] = goal_type.value

        try:
            db_profile = await UserProfileCrud.create_profile_db(db, dict_profile)
            await db.commit()
            await db.refresh(db_profile)
            return db_profile

        except Exception:
            await db.rollback()
            raise

    # read
    @staticmethod
    async def get_profile(db: AsyncSession, user_id: str):
        db_profile = await UserProfileCrud.get_profile_db(db, user_id)
        if not db_profile:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Found"
            )
        # age계산
        today = date.today()
        birth = db_profile.birthdate
        age = today.year - birth.year

        # age 필드 추가
        # model_validate -> model_copy(update={"key":value})
        # age field를 추가할 가장 간단한방식

        # db_profile(orm): age(x) -> pydantic -> 복사후 새로운 응답용모델생성
        pydantic_profile = UserProfileRead.model_validate(db_profile)
        #
        profile_response = pydantic_profile.model_copy(update={"age": age})

        return profile_response

    # update    #UserProfile orm객체
    @staticmethod
    async def update_profile(db: AsyncSession, user_id: int, profile: UserProfile):

        # patch(요청에서 전달된 필드만 업데이트)
        dict_profile = profile.model_dump(exclude_unset=True)
        print(type(dict_profile))
        # 프론트 필요시 (enum validation err 예외처리 추가)

        # db이상현상 방지 예외처리 / 문제발생시 - rollback()
        try:
            updated_profile = await UserProfileCrud.update_profile_db(
                db, user_id, dict_profile
            )

            if not updated_profile:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"프로필정보가 없습니다",
                )

            # db쓰기 확정 / refresh
            await db.commit()
            await db.refresh(updated_profile)
            # age계산
            today = date.today()
            birth = updated_profile.birthdate
            age = today.year - birth.year

            # db_profile(orm): age(x) -> pydantic -> 복사후 새로운 응답용모델생성
            pydantic_profile = UserProfileRead.model_validate(updated_profile)
            #
            profile_response = pydantic_profile.model_copy(update={"age": age})

            return profile_response

        except Exception:
            await db.rollback()
            raise
