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
from typing import List
from enum import Enum
from datetime import date

# 건강 및 식이 제한정보 user_health_conditions
# 최소 기능 구현상태 - error 터지면 아마도 500 -> 일단 traceback으로 처리 # TODO: 추후 예외처리 로직 추가예정


class HealthConditionService:
    # --- healthcondition 개별 ---
    # create condition
    @staticmethod
    async def create_one_condition(
        db: AsyncSession, user_id: int, condition: HealthConditionCreate
    ):
        dict_condition = condition.model_dump()
        # user_id필드 추가
        dict_condition["user_id"] = user_id

        try:
            db_condition = await HealthConditionCrud.create_one_condition_db(
                db, dict_condition
            )
            await db.commit()
            await db.refresh(db_condition)
            return db_condition

        except Exception:
            await db.rollback()
            raise

    # read
    @staticmethod
    async def get_condition(db: AsyncSession, user_id: int):
        db_condition = await HealthConditionCrud.get_condition_db(db, user_id)
        if not db_condition:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Found"
            )

        return db_condition

    # read_all_conditions
    async def get_all_conditions(db: AsyncSession, user_id: int) -> List[str]:
        db_conditions = await HealthConditionCrud.get_all_condition_db(db, user_id)
        return db_conditions

    # update 나중에 단일 엔드포인트시 필요

    # delete
    @staticmethod
    async def delete_condition(db: AsyncSession, user_id: int):
        try:
            db_conditions = await HealthConditionCrud.delete_condition_db(db, user_id)
            if not db_conditions:
                raise HTTPException(status_code=404, detail="Not found")

            await db.commit()
            return True

        except Exception:
            await db.rollback()
            raise

    # --------------------------------------------
    # ProfileForm CRUD
    # --------------------------------------------
    # create condition bulk (profile 필드추가용)
    @staticmethod
    async def create_condition_list(
        db: AsyncSession, user_id: int, conditions: list[str]
    ) -> list[str]:
        """
        conditions= list[str]
        """
        print("user_id:", user_id)

        # condition = None -> db변경없이 종료
        if not conditions:
            return []

        # dict_condition = conditions.model_dump()
        condition_list = conditions
        dict_conditions = [
            {"user_id": user_id, "conditions": con} for con in condition_list
        ]

        try:
            # db 저장위해 crud로 객체넘김
            db_condition_orm_list = await HealthConditionCrud.create_all_conditions_db(
                db, dict_conditions
            )

            # response 용 가공 [ormobj] -> list[str]
            condition_str_list = [orm.conditions for orm in db_condition_orm_list]
            await db.commit()
            return condition_str_list  # list[str] (profile쪽에서 호출)

        except Exception:
            # db 보호 1차 안전장치
            await db.rollback()
            raise

    # read -> 기존 함수 사용(profileform service)

    # update(replace all)
    @staticmethod
    async def update_condition_form(
        db: AsyncSession, user_id: int, conditions: list[str]
    ):

        # conditions: []
        if conditions == []:
            try:
                await HealthConditionCrud.delete_all_conditions_db(db, user_id)
                await db.commit()
                # not use optional / service에서 DTO반환
                return

            except Exception as e:
                await db.rollback()
                print(f"[SERVICE ERROR][함수명] {e}")
                raise

        # conditions: ["a"]
        try:
            await HealthConditionCrud.delete_all_conditions_db(db, user_id)
            condition_list = conditions
            dict_conditions = [
                {"user_id": user_id, "conditions": con} for con in condition_list
            ]
            await HealthConditionCrud.create_all_conditions_db(db, dict_conditions)
            await db.commit()
            return

        except Exception:
            # db 보호 1차 안전장치
            await db.rollback()
            raise
