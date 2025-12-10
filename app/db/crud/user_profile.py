from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.user_profile import UserProfile
from app.db.schemas.user_profile import (
    UserProfileCreate,
    ProfileFormCreate,
    ProfileFormRead,
)
from typing import Optional

# UserProfile, front(userInfo)
# User:UserProfile = 1:1


class UserProfileCrud:
    # create
    @staticmethod
    async def create_profile_db(db: AsyncSession, profile: dict):

        # model_dump (pytdantic-> dict) : service로이동(user_id필드 추가)
        db_profile = UserProfile(**profile)
        db.add(db_profile)
        await db.flush()  # PK생성, DB내 query insert
        return db_profile

    # read my profile
    @staticmethod
    async def get_profile_db(db: AsyncSession, user_id: int):
        result = await db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    # update
    @staticmethod
    async def update_profile_db(
        db: AsyncSession, user_id: int, update_profile: dict
    ) -> UserProfile | None:
        result = await db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        db_profile = result.scalar_one_or_none()

        for i, j in update_profile.items():
            setattr(db_profile, i, j)

        await db.flush()
        return db_profile

    # delete 필요 x : 유저삭제시에만 프로필 삭제됨  1:1 cascade
    # admin 권한 + page 구현시 추가
