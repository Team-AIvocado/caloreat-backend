from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.schemas.user_health_condition import (
    HealthConditionCreate,
    HealthConditionUpdate,
    HealthConditionRead,
)
from app.db.models.user import User
from app.db.models.user_health_condition import HealthCondition
from app.db.crud.user_health_condition import HealthConditionCrud

from enum import Enum
from datetime import date

# 건강 및 식이 제한정보 user_health_conditions
# 최소 기능 구현상태 - error 터지면 아마도 500 -> 일단 traceback으로 처리 # TODO: 추후 예외처리 로직 추가예정


class HealthConditionService:
    @staticmethod
    async def create_condition(
        db: AsyncSession, user_id: int, conditions: HealthConditionCreate
    ):
        # conditions input = None이면 db insert 자체를 차단
        if not conditions.conditions:
            return []

        dict_condition = conditions.model_dump()
        # add user_id from auth context (DB insert용)
        dict_condition["user_id"] = user_id

        try:
            db_condition = await HealthConditionCrud.create_condition_db(
                db, dict_condition
            )
            await db.commit()
            await db.refresh(db_condition)
            return db_condition

        except Exception:
            await db.rollback()
            raise

    @staticmethod
    async def read_condition(db: AsyncSession, user_id: int):
        pass

    @staticmethod
    async def update_condition(
        db: AsyncSession, user_id: int, conditions: HealthConditionUpdate
    ):
        pass

    @staticmethod
    async def delete_condition(db, user_id):
        pass
