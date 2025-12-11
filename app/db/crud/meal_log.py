from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.meal_log import MealLog
from app.db.models.meal_item import MealItem
from sqlalchemy.orm import selectinload
from sqlalchemy import select, cast, Date, delete, CursorResult


# MealLog
# 식단저장, 식단조회, 식단삭제


class MealLogCrud:
    """
    MealLog 및 MealItem에 대한 순수 DB CRUD 작업만 담당
    **kwargs 언패킹을 사용하여 딕셔너리 기반으로 모델을 생성
    """

    # --create--
    # meal_log
    # TODO: orm handling 변경 중복방지 + 안정성증가
    @staticmethod
    async def create_meal_log_db(db: AsyncSession, log_data: dict) -> MealLog:
        """
        MealLog 레코드 생성
        :param log_data: MealLog 모델 생성에 필요한 데이터 딕셔너리 (user_id 포함)
        """
        new_log = MealLog(**log_data)
        db.add(new_log)
        await db.flush()  # ID 생성을 위해 flush
        await db.refresh(new_log)
        return new_log

    # meal_item
    @staticmethod
    async def create_meal_items_db(
        db: AsyncSession, items_data: list[dict]
    ) -> list[MealItem]:
        """
        MealItem 레코드 리스트 생성
        :param items_data: MealItem 모델 생성에 필요한 데이터 딕셔너리 리스트 (meal_log_id 포함)
        """
        new_items = []
        for item_dict in items_data:
            new_item = MealItem(**item_dict)
            db.add(new_item)
            new_items.append(new_item)

        return new_items  # TODO: read 구현 후 DTO처리 고민 필요

    # --read--
    # 현재로그인한 유저의 해당날짜의 식단(아침,점심,저녁)조회
    @staticmethod
    async def get_meal_logs_db(
        db: AsyncSession, user_id: int, date=None
    ) -> list[MealLog]:
        # 날짜별 조회 전용 함수: 날짜가 없으면 빈 리스트 반환
        if not date:
            return []

        # 기본 쿼리 구성 + 날짜 필터링 필수
        result = await db.execute(
            select(MealLog)
            .where(MealLog.user_id == user_id)
            .where(cast(MealLog.eaten_at, Date) == date)  # datetime -> Date(YYYY-MM-DD)
            .options(selectinload(MealLog.meal_items))
            .order_by(MealLog.eaten_at.desc())
        )

        return result.scalars().all()

    @staticmethod
    async def get_meal_log_by_id_db(db: AsyncSession, meal_id: int) -> MealLog | None:
        """
        특정 식단 단건 조회 (MealItem 포함)
        """
        result = await db.execute(
            select(MealLog)
            .where(MealLog.id == meal_id)
            .options(selectinload(MealLog.meal_items))
        )
        return result.scalar_one_or_none()

    # --delete--
    @staticmethod
    async def delete_meal_log_db(db: AsyncSession, meal_id: int, user_id: int) -> bool:
        """
        MealLog 삭제 (ON DELETE CASCADE로 MealItem도 자동 삭제됨)
        :param meal_id: 삭제할 식단 ID
        :param user_id: 소유자 확인용 User ID
        :return: 삭제 성공 여부 (True: 삭제됨, False: 대상 없음)
        """
        # ORM 객체 생성 없이 조건에 맞는 레코드 바로 삭제
        result = await db.execute(
            delete(MealLog).where(MealLog.id == meal_id, MealLog.user_id == user_id)
        )

        # rowcount는 “실제로 삭제된 결과”를 정확하게 보증
        return result.rowcount > 0

    # --update-- direct query -> orm handling 변경
    @staticmethod
    async def update_meal_log_db(
        db: AsyncSession, meal_id: int, user_id: int, update_data: dict
    ) -> MealLog | None:
        """
        MealLog 메타데이터(meal_type, eaten_at 등) 업데이트 (Read-Modify-Update 패턴)
        :return: 업데이트된 MealLog 객체 (없거나 권한 없으면 None)
        """
        # 1. 조회 (SELECT)
        result = await db.execute(
            select(MealLog).where(MealLog.id == meal_id, MealLog.user_id == user_id)
        )
        meal_log = result.scalar_one_or_none()

        if not meal_log:
            return None

        # 2. 수정 (Apply Changes)
        for key, value in update_data.items():
            if hasattr(meal_log, key):
                setattr(meal_log, key, value)

        # 3. 반영 (Flush -> UPDATE Query)
        await db.flush()
        return meal_log

    @staticmethod
    async def delete_meal_items_by_log_id(db: AsyncSession, meal_log_id: int):
        """
        특정 MealLog에 속한 모든 MealItem 삭제 (Full Replace 준비)
        """

        await db.execute(delete(MealItem).where(MealItem.meal_log_id == meal_log_id))
