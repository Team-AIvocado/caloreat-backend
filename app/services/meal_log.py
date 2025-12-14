from fastapi import HTTPException, status, UploadFile, File
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
from app.db.schemas.meal_log import MealLogCreate, MealLogUpdate
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
    ) -> MealLogRead:
        # 1. 중복 검사 (TODO: 중복 시 409 에러 발생 로직 추가 필요)
        # - user_id, eaten_at(YYYY-MM-DD), meal_type 확인

        # 2. 이미지 처리 (tmp -> S3)
        # External Service 호출은 트랜잭션 외부에서 처리하는 것이 좋음 (시간 소요)
        image_urls = await MealImageService.upload_tmp_images_to_s3(
            meal_create.tmp_image_ids
        )

        # 3. 데이터 준비 (Python Logic)
        log_data = meal_create.model_dump(include={"meal_type", "eaten_at"})
        log_data["user_id"] = current_user_id
        log_data["image_urls"] = image_urls

        # ORM Relationship 활용을 위한 items 데이터 준비 (meal_log_id 매핑 불필요)
        items_data = [item.model_dump() for item in meal_create.meal_items]

        # 4. DB 트랜잭션 시작 (시스템 예외 처리)
        try:
            # MealLog + MealItems 동시 생성 (ORM)
            # Service에서 ID에 접근할 필요가 없어져 MissingGreenlet 원천 차단
            new_log = await MealLogCrud.create_meal_log_db(db, log_data, items_data)

            # [Fix] commit 이후에는 new_log 객체가 expire되므로, ID를 미리 추출해야 함 ★
            # orm객체는 시한부인생임 세션닫히면 사망함
            new_log_id = new_log.id

            # 트랜잭션 확정
            await db.commit()

            # re-query
            # 생성된 ID로 전체 데이터를 다시 조회 완벽한 상태의 객체 확보: orm 스타일
            # 미리 추출한 ID(int)를 사용하여 안전하게 조회 ★
            created_log = await MealLogCrud.get_meal_log_by_id_db(db, new_log_id)

            # 중요기능이므로 ORM -> DTO 변환 후 반환 (안정성, 협업 명시성)
            pydantic_created_log = MealLogRead.model_validate(created_log)
            return pydantic_created_log

        except Exception as e:
            await db.rollback()
            print(f"[SERVICE ERROR][create_meal_log] {e}")
            raise

    # update (PUT)
    # TODO: update logic review필요 찝집함, 헬퍼함수 분리 refactoring 고려(가독성)
    @staticmethod
    async def update_meal_log(
        db: AsyncSession, user_id: int, meal_id: int, update_req: MealLogUpdate
    ) -> MealLog:
        """
        식단(MealLog) 전체 수정 (Full Replace)
        1. MealLog 메타데이터 (type, time) 업데이트 (이미지 수정 불가)
        2. 기존 MealItem 전체 삭제
        3. 새 MealItem 전체 생성
        """
        # 1. MealLog 업데이트 (메타데이터만)
        # items는 별도 처리하므로 제거
        update_data = update_req.model_dump(
            exclude={"meal_items", "image_urls"}, exclude_unset=True
        )

        # Log 업데이트 시도 (존재 여부 및 소유권 확인 겸용)
        # CRUD 내부에서 SELECT -> setattr -> flush 수행
        updated_log = await MealLogCrud.update_meal_log_db(
            db, meal_id, user_id, update_data
        )

        if not updated_log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meal log not found or permission denied",
            )

        # 2. MealItems 교체 (Full Replace) 트랜잭션
        try:
            # 기존 아이템 전량 삭제
            await MealLogCrud.delete_meal_items_by_log_id(db, meal_id)

            # 새 아이템 데이터 준비
            new_items_data = []
            for item in update_req.meal_items:
                item_dict = item.model_dump()
                item_dict["meal_log_id"] = meal_id
                new_items_data.append(item_dict)

            # 새 아이템 일괄 생성
            if new_items_data:
                await MealLogCrud.create_meal_items_db(db, new_items_data)

            # 3. 트랜잭션 확정
            await db.commit()

            # Response를 위해 관계 데이터(meal_items)를 포함하여 다시 조회
            return await MealLogCrud.get_meal_log_by_id_db(db, meal_id)

        except Exception as e:
            await db.rollback()
            print(f"[SERVICE ERROR][update_meal_log] {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while updating the meal log",
            )

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
