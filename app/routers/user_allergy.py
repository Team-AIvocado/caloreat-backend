from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user, get_user_id
from app.core.auth import set_login_cookies, set_access_cookie

from app.db.database import get_db
from app.db.models.user import User
from app.db.models.user_health_condition import HealthCondition
from app.db.schemas.user_health_condition import (
    HealthConditionCreate,
    HealthConditionRead,
    HealthConditionUpdate,
)
from app.services.user_health_condition import HealthallergyService

from typing import Annotated, List


router = APIRouter(prefix="/users/me/heatlh-allergies", tags=["Allergy"])

#


# add allerg
@router.post("/", response_model=HealthConditionRead)
async def create_allergy_endpoint(
    allergys: HealthConditionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = current_user.id
    new_profile = await HealthallergyService.create_allergy(db, user_id, allergys)
    return new_profile


# read allergys
@router.get("/", response_model=HealthConditionRead)
async def get_allergy_endpoint(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    user_id = current_user.id
    db_allergys = await HealthallergyService.get_allergy(db, user_id)
    return db_allergys


# update allergys
@router.patch("/", response_model=HealthConditionRead, summary="건강정보 수정")
async def update_allergy_endpoint(
    allergys: HealthConditionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = current_user.id
    db_allergy = await HealthallergyService.update_allergy(db, user_id, allergys)
    return db_allergy


#
# admin api, 권한주입은 따로 함수를구현 후 생성해야함
@router.delete("/{user_id}", response_model=HealthConditionRead)
async def delete_allergy_endpoint(user_id: int, db: AsyncSession = Depends(get_db)):
    await HealthallergyService.delete_allergy(db, user_id)
    return {"deleted": True, "deleted_user_id": {user_id}}


# delete - allergys, allergy은 oncascade / admin 용
# TODO: admin 활성화 후 authorization 제한 필요
# @router.delete("/{allergy_id}", summary="유저컨디션정보 관리")
# async def delete_allergy_endpoint(
#     current_user_id: int = Depends(get_user_id), db: AsyncSession = Depends(get_db)
# ):
#     await HealthallergyService.delete_allergy(db, current_user_id)
#     return {"deleted": True, "deleted_user_id": current_user_id}
