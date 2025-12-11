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

from app.db.schemas.meal_log import MealLogRead
from app.db.schemas.meal_log import MealLogCreate
from app.db.crud.meal_log import MealLogCrud
from app.services.meal_image import MealImageService

# MealLog 저장 매우 복잡
# 1. 중복 검사
# 2. 이미지 처리
# 3. 데이터 준비
# 4. DB 트랜잭션 시작
# 5. MealLog 생성
# 6. MealItem 데이터에 ID 매핑
# 7. MealItem 일괄 생성
# 8. 트랜잭션 확정


class MealLogService:
    # create
    @staticmethod
    async def create_meal_log(
        db: AsyncSession, current_user_id: int, meal_create: MealLogCreate
    ):
        # 1. 중복 검사 (TODO: 중복 시 409 에러 발생 로직 추가 필요)
        # - user_id, eaten_at(YYYY-MM-DD), meal_type 확인

        # 2. 이미지 처리 (tmp -> S3)
        # External Service 호출은 트랜잭션 외부에서 처리하는 것이 좋음 (시간 소요)
        image_urls = await MealImageService.upload_tmp_images_to_s3(
            meal_create.tmp_image_ids
        )

        # 3. 데이터 준비 (Pure Python Logic)
        log_data = meal_create.model_dump(include={"meal_type", "eaten_at"})
        log_data["user_id"] = current_user_id
        log_data["image_urls"] = image_urls

        items_data = []
        # log_id는 아직 모르지만, 객체 생성 후 할당 예정

        # 4. DB 트랜잭션 시작 (시스템 예외 처리)
        try:

            # MealLog 생성 (Flush로 ID 획득)
            new_log = await MealLogCrud.create_meal_log_db(db, log_data)

            # MealItem 데이터에 ID 매핑
            for item in meal_create.meal_items:
                item_dict = item.model_dump()
                item_dict["meal_log_id"] = new_log.id
                items_data.append(item_dict)

            # MealItem 일괄 생성
            await MealLogCrud.create_meal_items_db(db, items_data)

            # 트랜잭션 확정
            await db.commit()
            await db.refresh(new_log)
            return new_log

        except Exception as e:
            await db.rollback()
            print(f"[SERVICE ERROR][create_meal_log] {e}")
            raise

    # read
    @staticmethod
    async def read_meal_log(
        db: AsyncSession, user_id: int, date: date | None
    ) -> list[MealLog]:
        """
        MealLog 조회
        - 단순 조회이므로 try-except 불필요 (전역 핸들러 위임)
        """
        if date is None:
            return []

        return await MealLogCrud.get_meal_logs_db(db, user_id, date)

    # delete
    @staticmethod
    async def delete_meal_log(db: AsyncSession, user_id: int, meal_id: int) -> bool:
        """
        식단(MealLog) 삭제
        - 본인 소유 확인 및 삭제 (CRUD 위임)
        - DB Transaction Commit
        """
        # 1. 삭제 시도 (CRUD 호출)
        is_deleted = await MealLogCrud.delete_meal_log_db(db, meal_id, user_id)

        # 2. 비즈니스 로직 분기: 대상이 없거나 권한 부족
        if not is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meal log not found or permission denied",
            )

        # 3. 변경 확정 (시스템 예외 처리)
        try:
            await db.commit()
            return True  # 성공적으로 삭제됨

        except Exception as e:
            await db.rollback()
            print(f"[SERVICE ERROR][delete_meal_log] {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while deleting the meal log",
            )
