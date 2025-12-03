from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.engine import CursorResult

# models
from app.db.models.meal_unused import MealImage

# schemas
from app.db.schemas.meal_image import (
    MealImageResponse,
)
from typing import Optional, List


class MealImageCrud:
    @staticmethod
    async def create(db, user_id, payload):
        obj = MealImage(user_id=user_id, **payload.model_dump())
        db.add(obj)
        return obj

    @staticmethod
    async def get(db, user_id):
        q = select(MealImage).where(MealImage.user_id == user_id)
        return (await db.execute(q)).scalar_one_or_none()

    @staticmethod
    async def update(db, user_id, payload):
        q = select(MealImage).where(MealImage.user_id == user_id)
        obj = (await db.execute(q)).scalar_one()
        for k, v in payload.model_dump(exclude_unset=True).items():
            setattr(obj, k, v)
        return obj

    @staticmethod
    async def delete(db, user_id):
        q = delete(MealImage).where(MealImage.user_id == user_id)
        await db.execute(q)
