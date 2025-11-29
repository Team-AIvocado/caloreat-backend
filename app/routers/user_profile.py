from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.auth import get_current_user

from app.db.database import get_db
from app.db.models.user import User
from app.db.models.user_profile import UserProfile
from app.db.crud.user_profile import UserProfileCrud
from app.db.schemas.user_profile import (
    UserProfileCreate,
    UserProfileRead,
    UserProfileUpdate,
)

from app.services.user import UserService
from app.services.user_profile import UserProfileService

from typing import Annotated, List

# URL path 언더스코어 금지원칙 user_profile -> user-profile -> profile
router = APIRouter(prefix="/users/me/profile", tags=["UserProfile"])

# TODO: db, current_user deps wrapping 정리(가독성)
# --- profile 단일조회 ---


# create (userinfo 입력)
@router.post(
    "/",
    response_model=UserProfileCreate,
    summary="Create:신체정보+목표 입력",
    description="""                
          프로필 단일생성, conditions(질병,조건) 미포함
             """,
)
async def create_profile_endpoint(
    profile: UserProfileCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = current_user.id
    new_profile = await UserProfileService.create_profile(db, user_id, profile)
    return new_profile


# read (신체정보+목표 표시)
@router.get("/", response_model=UserProfileRead, summary="Read:신체정보+목표 표시")
async def get_profile_endpoint(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    user_id = current_user.id
    db_profile = await UserProfileService.get_profile(db, user_id)
    return db_profile


# update (신체정보+목표 업데이트)
@router.patch("/", response_model=UserProfileRead, summary="Update:신체정보+목표 수정")
async def update_profile_endpoint(
    profile: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = current_user.id
    db_profile = await UserProfileService.update_profile(db, user_id, profile)
    return db_profile


# delete - profile은 oncascade delte/ TODO: admin 추가시 구현
