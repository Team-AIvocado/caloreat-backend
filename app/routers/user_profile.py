from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.auth import (
    get_current_user,
    get_user_id,
)  # get_user_id는 왠만하면 x DB중복조회 등

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

# URL path 언더스코어 금지원칙 user_profile -> user-profile
router = APIRouter(prefix="/users/me/profile", tags=["UserProfile"])


# create (userinfo 입력)    #TODO: birthdate 회원가입 이동 논의필요
@router.post(
    "/",
    response_model=UserProfileCreate,
    summary="Create:신체정보+목표 입력",
    description="""                
                goal_type(str): \n
                - 'loss':체중 감량 \n
                - 'maintain':체중 유지 \n
                - 'gain' : 증량 \n
                
                birthdate(date): 나이계산용, 회원가입이동필요?             
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


# delete - profile, condition은 oncascade
