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


class AllergyService:
    @staticmethod
    async def create_allergy():
        pass

    @staticmethod
    async def read_allergy(db: AsyncSession, user_id: int):
        pass

    @staticmethod
    async def update_allergy(db: AsyncSession, user_id: int, allergies):
        pass

    @staticmethod
    async def delete_allergy(db, user_id):
        pass
