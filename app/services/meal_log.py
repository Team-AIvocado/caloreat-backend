from fastapi import HTTPException, status, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.schemas.meal_image import (
    MealImageResponse,
)
from app.db.models.user import User

# from app.db.models.meal_unused import MealImage

# from app.db.crud.meal_image import MealImageCrud
from typing import List
from enum import Enum
from datetime import date


from app.db.models.meal_log import MealLog
from app.db.models.meal_item import MealItem
from app.db.schemas.meal_log import MealLogCreate


class MealLogService:
    @staticmethod
    async def create_meal_log(
        db: AsyncSession, meal_create: MealLogCreate, current_user_id: int
    ):
        """
        식단(MealLog) 및 상세 음식(MealItem)을 DB에 저장하는 스켈레톤
        """
        try:
            # 1. MealLog (부모) 저장
            # MealLog 객체 생성 (사용자 ID 및 요청 데이터 매핑)
            # new_log = MealLog(
            #     user_id=current_user_id,
            #     meal_type=meal_create.meal_type,
            #     eaten_at=meal_create.eaten_at,
            #     image_urls=meal_create.image_urls
            # )
            # db.add(new_log)
            # await db.flush()  # DB에 임시 반영하여 new_log.id 생성
            # await db.refresh(new_log)  # 생성된 ID 등 최신 정보 로드

            # 2. MealItem (자식) 반복 저장
            # 반복문으로 각 음식 아이템 처리
            # for item in meal_create.meal_items:
            #     new_item = MealItem(
            #         meal_log_id=new_log.id,  # 생성된 부모 ID 연결
            #         foodname=item.foodname,
            #         quantity=item.quantity,
            #         nutritions=item.nutritions  # JSON 형태 그대로 저장
            #     )
            #     db.add(new_item)

            # 3. 트랜잭션 확정 (Commit)
            # 모든 작업 성공 시 커밋
            # await db.commit()

            # 4. 결과 반환
            # 저장된 MealLog 객체 반환 (스키마에 맞춰 응답)
            # return new_log
            pass

        except Exception as e:
            # 에러 발생 시 롤백 (데이터 무결성 보장)
            await db.rollback()
            raise e
