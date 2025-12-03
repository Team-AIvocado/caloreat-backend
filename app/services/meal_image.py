from fastapi import HTTPException, status, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.schemas.meal_image import (
    MealImageResponse,
)
from app.db.models.user import User
from app.db.models.meal_unused import MealImage
from app.db.crud.meal import MealImageCrud
from typing import List
from enum import Enum
from datetime import date


# Meal Service
class MealImageService:
    @staticmethod
    async def create(db: AsyncSession, user_id: int, file: UploadFile):
        pass
        # orm = await MealImageCrud.create(db, user_id, file)
        # await db.commit()
        # await db.refresh(orm)
        # return orm

    @staticmethod
    async def get(db, user_id):
        orm = await MealImageCrud.get(db, user_id)
        return orm

    @staticmethod
    async def update(db, user_id, payload):
        orm = await MealImageCrud.update(db, user_id, payload)
        await db.commit()
        await db.refresh(orm)
        return orm

    @staticmethod
    async def delete(db, user_id):
        await MealImageCrud.delete(db, user_id)
        await db.commit()
