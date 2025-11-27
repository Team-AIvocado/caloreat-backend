from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.user_health_condition import HealthCondition
from app.db.schemas.user_health_condition import (
    HealthConditionCreate,
    HealthConditionUpdate,
    HealthConditionRead,
)
from typing import Optional, List


# 건강 및 식이 제한정보 user_health_conditions
# CRUD db조작 쿼리만 , transaction(x) -> service로 책임 분리
class HealthConditionCrud:
    # create conditions  #TODO : condition 스키마타입 변경 후 이름변경(복수->단수)
    @staticmethod
    async def create_condition_db(db: AsyncSession, conditions: dict):
        db_conditions = HealthCondition(**conditions)
        db.add(db_conditions)
        await db.flush()  # PK생성, DB내 query insert
        return db_conditions

    # read
    @staticmethod
    async def update_condition_db(db: AsyncSession, user_id: int):
        result = await db.execute(
            select(HealthCondition).where(HealthCondition.user_id == user_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def read_condition_db(
        db: AsyncSession, user_id: int, updated_condition: dict
    ) -> HealthCondition | None:
        result = await db.execute(
            select(HealthCondition).where(HealthCondition.user_id == user_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def delete_condition_db(db: AsyncSession, user_id: int) -> bool:
        db_condition = await db.get(HealthCondition, user_id)
        # 실패시 조기종료
        if not db_condition:
            raise HTTPException(status_code=404, detail="Not found")

        await db.delete(db_condition)
        await db.flush()  # db에 쿼리문날림/ 롤백가능
        return True
