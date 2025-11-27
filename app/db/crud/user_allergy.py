from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.user_profile import UserProfile
from app.db.schemas.user_profile import UserProfileCreate
from typing import Optional, List


# 건강 및 식이 제한정보 user_health_conditions
class AllergyCrud:
    # create condition
    @staticmethod
    async def create_condition_db():
        pass

    @staticmethod
    async def read_condition_db():
        pass

    @staticmethod
    async def update_condition_db():
        pass

    @staticmethod
    async def delete_condition_db():
        pass
