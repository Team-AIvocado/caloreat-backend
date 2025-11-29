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
    ProfileFormCreate,
    ProfileFormUpdate,
    ProfileFormResponse,
    ProfileFormRead,
)
from app.services.user import UserService
from app.services.user_profile import UserProfileService
from app.services.user_profile_form import ProfileFormService


from typing import Annotated, List

router = APIRouter(prefix="/users/me/profile", tags=["UserProfile"])

# --- ProfileForm endpoints ---
# ux고려, 유지보수, 확장성 고려 통합엔드포인트 분리


# create
@router.post(
    "/form",
    response_model=ProfileFormResponse,
    summary="Create:condition 속성 포함 프로필생성",
)
async def create_profile_endpoint(
    profile_form: ProfileFormCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = current_user.id
    new_profile = await ProfileFormService.create_profile_form(
        db, user_id, profile_form
    )
    return new_profile


# get
@router.get("/form", response_model=ProfileFormRead)
async def get_profile_endpoint(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    user_id = current_user.id
    db_profile_form = await ProfileFormService.read_profile_form(db, user_id)
    return db_profile_form


# update
# delete
