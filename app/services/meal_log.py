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
from app.db.crud.meal_log import MealLogCrud


class MealLogService:
    @staticmethod
    async def create_meal_log(
        db: AsyncSession, current_user_id: int, meal_create: MealLogCreate
    ):
        try:
            # 1. 이미지 처리 (tmp -> S3)
            # MealImageService에 위임하여 S3 업로드 및 URL 획득
            from app.services.meal_image import MealImageService

            image_urls = await MealImageService.upload_tmp_images_to_s3(
                meal_create.tmp_image_ids
            )

            # 2. CRUD 계층 호출을 위한 데이터 준비 (Dictionary 변환)
            # MealLog 데이터 준비
            log_data = meal_create.model_dump(include={"meal_type", "eaten_at"})
            log_data["user_id"] = current_user_id
            log_data["image_urls"] = image_urls

            # MealLog 생성 (CRUD 호출)

            new_log = await MealLogCrud.create_meal_log_db(db, log_data)

            # MealItem 데이터 준비
            items_data = []
            for item in meal_create.meal_items:
                item_dict = item.model_dump()
                item_dict["meal_log_id"] = new_log.id
                items_data.append(item_dict)

            # MealItem 일괄 생성 (CRUD 호출)
            await MealLogCrud.create_meal_items_db(db, items_data)

            # 3. 트랜잭션 확정
            await db.commit()
            await db.refresh(new_log)
            return new_log

        except Exception as e:
            await db.rollback()
            print(f"[SERVICE ERROR][create_meal_log] {e}")
            raise
