from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user, get_user_id
from app.core.auth import set_login_cookies, set_access_cookie

from app.db.database import get_db
from app.db.models.user import User
from app.db.crud.user import UserCrud

from app.services.user import UserService

from typing import Annotated, List


router = APIRouter(prefix="user/me/heatlh-conditions", tags=["HealthCondition"])

# POST /users/me/health-conditions
# GET /users/me/health-conditions – 컨디션 데이터 조회

# PATCH /users/me/health-conditions – 특정 필드만 수정
