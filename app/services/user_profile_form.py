from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.schemas.user_profile import (
    ProfileFormUpdate,
    ProfileFormCreate,
    ProfileFormRead,
)
from app.db.models.user_profile import UserProfile
from app.db.models.user_health_condition import HealthCondition
from app.db.crud.user_profile import UserProfileCrud

from app.services.user_health_condition import HealthConditionService
from app.services.user_profile import UserProfileService

# from app.services.user_allergy import AllergyService

import copy
from enum import Enum
from datetime import date


# 가독성문제로 파일분리+ helper함수생성
class ProfileFormService:
    # helpers
    # input-> dict
    @staticmethod
    def make_profile_dict(user_id: int, profile_form: ProfileFormCreate) -> dict:
        """
        칼럼추가를위한 dict작업 함수 , ./ line 31
        """
        # conditions칼럼제외  pop() << model_dump(exclude={"conditions"})
        dict_form = profile_form.model_dump(exclude={"conditions"})
        dict_form["user_id"] = user_id

        goal_type = dict_form.get("goal_type")
        if isinstance(goal_type, Enum):
            dict_form["goal_type"] = goal_type.value
        return dict_form

    # response 필드 변환
    @staticmethod
    def make_response_model(db_profile, conditions):
        """
        db_profile: orm -> return copied pydantic response model ./ line46
        """
        pydantic_profile = ProfileFormRead.model_validate(db_profile)
        response_profile = pydantic_profile.model_copy(
            update={"conditions": conditions}
        )
        return response_profile

    # -------------------------------------
    # CRUD
    # -------------------------------------
    # create form
    @staticmethod
    async def create_profile_form(
        db: AsyncSession, user_id: int, profile_form: ProfileFormCreate
    ):
        # profile_form: pydantic -> dict
        dict_profile = ProfileFormService.make_profile_dict(user_id, profile_form)

        # condition속성 db저장(condition)
        conditions = await HealthConditionService.create_condition_list(
            db, user_id, profile_form.conditions
        )

        try:
            db_profile = await UserProfileCrud.create_profile_db(db, dict_profile)
            response_profileform = ProfileFormService.make_response_model(
                db_profile, conditions
            )

            await db.commit()
            await db.refresh(db_profile)
            return response_profileform

        except Exception:
            await db.rollback()
            raise

    # read: add conditions
    @staticmethod
    async def read_profile_form(db: AsyncSession, user_id: int):
        db_profile = await UserProfileService.get_profile(db, user_id)  # pydantic
        conditions = await HealthConditionService.get_all_conditions(
            db, user_id
        )  # list[str]

        # profile pydantic-> dict
        dict_profile = db_profile.model_dump()
        dict_profile["conditions"] = conditions

        response_form = ProfileFormRead(**dict_profile)
        return response_form
