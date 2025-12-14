from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.engine import CursorResult

from app.db.models.user_health_condition import HealthCondition
from app.db.schemas.user_health_condition import (
    HealthConditionCreate,
    HealthConditionUpdate,
    HealthConditionRead,
)
from typing import Optional


# 건강 및 식이 제한정보 user_health_conditions
# CRUD db조작 쿼리만 , transaction(x) -> service로 책임 분리
class HealthConditionCrud:
    # 단일 condition 조회 (1row)
    @staticmethod
    async def create_one_condition_db(db: AsyncSession, conditions: dict):
        # model_dump (pytdantic-> dict) : service로이동(user_id필드 추가)
        db_profile = HealthCondition(**conditions)
        db.add(db_profile)
        await db.flush()  # PK생성, DB내 query insert
        return db_profile

    # read
    @staticmethod
    async def get_condition_db(db: AsyncSession, user_id: int):
        result = await db.execute(
            select(HealthCondition).where(HealthCondition.user_id == user_id)
        )
        return result.scalar_one_or_none()

    # read & return list
    @staticmethod
    async def get_all_condition_db(db: AsyncSession, user_id: int) -> list[str]:
        result = await db.execute(
            select(HealthCondition.conditions).where(HealthCondition.user_id == user_id)
        )
        return result.scalars().all()

    # delete {user_id}
    @staticmethod
    async def delete_condition_db(db: AsyncSession, user_id: int) -> bool:
        print("input_user_id:", user_id)

        result = await db.execute(
            select(HealthCondition).where(HealthCondition.user_id == user_id)
        )
        db_conditions = result.scalar_one_or_none()

        if not db_conditions:
            return False

        await db.delete(db_conditions)
        await db.flush()  # db에 쿼리문날림/ 롤백가능
        return True

    # ------------------------------------------------
    # ProfileForm용 함수
    # ------------------------------------------------

    # 다중 row db쓰기 후 rall return
    @staticmethod
    async def create_all_conditions_db(
        db: AsyncSession, conditions: list[dict]
    ) -> list[HealthCondition]:
        db_conditions = [HealthCondition(**condition) for condition in conditions]
        db.add_all(db_conditions)  # insert 순차실행
        await db.flush()  # PK생성, DB내 query insert

        return db_conditions  # orm list 객체 service로 반환

    # get -> profile

    # delete
    # delete : bulk delete
    @staticmethod
    async def delete_all_conditions_db(db: AsyncSession, user_id: int) -> bool:
        print("input_user_id:", user_id)
        # orm 생성없이 바로삭제
        result = await db.execute(
            delete(HealthCondition).where(HealthCondition.user_id == user_id)
        )
        # 커서사용 영향받은 row갯수 추출 :rowcount
        cursor: CursorResult = result
        deleted_count = cursor.rowcount

        return deleted_count > 0

    # update 필요x
