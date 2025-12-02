from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_user_id, get_current_user
from app.db.database import get_db

# 스키마
from app.db.schemas.meal import (
    MealImageCreate,
    MealImageUpdate,
    MealImageRead,
)

# 서비스
from app.services.meal import MealImageService


router = APIRouter(prefix="/meals", tags=["Meal"])


# meal image upload
@router.post("/upload", response_model=MealImageRead)
async def upload_image(
    payload: MealImageCreate,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await MealImageService.create(db, user_id, payload)


# @router.post("/", response_model=MealImageOut)
# async def create_x(
#     payload: MealImageCreate,
#     user_id: int = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db),
# ):
#     return await XService.create(db, user_id, payload)


# @router.get("/", response_model=MealImageOut)
# async def get_x(
#     user_id: int = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     return await XService.get(db, user_id)


# @router.patch("/", response_model=MealImageOut)
# async def update_x(
#     payload: MealImageUpdate,
#     user_id: int = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     return await XService.update(db, user_id, payload)

# @router.delete("/")
# async def delete_x(
#     user_id: int = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     await XService.delete(db, user_id)
#     return {"message": "deleted"}
