from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.meal_log import MealLog
from app.db.models.meal_item import MealItem
from sqlalchemy.orm import selectinload
from sqlalchemy import select, cast, Date


# MealLog
# 식단저장, 식단조회, 식단삭제


class MealLogCrud:
    """
    MealLog 및 MealItem에 대한 순수 DB CRUD 작업만 담당
    **kwargs 언패킹을 사용하여 딕셔너리 기반으로 모델을 생성
    """

    # --create--
    # meal_log DB쓰기
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

    # meal_item DB쓰기
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
    # 현재로그인한 유저의 날짜별 식단(아침,점심,저녁)조회
    @staticmethod
    async def get_meal_logs_db(
        db: AsyncSession, user_id: int, date=None
    ) -> list[MealLog]:
        # 날짜별 조회 전용 함수: 날짜가 없으면 빈 리스트 반환
        if not date:
            return []

        # 기본 쿼리 구성 (User Profile 스타일) + 날짜 필터링 필수
        result = await db.execute(
            select(MealLog)
            .where(MealLog.user_id == user_id)
            .where(cast(MealLog.eaten_at, Date) == date)
            .options(selectinload(MealLog.meal_items))
            .order_by(MealLog.eaten_at.desc())
        )

        return result.scalars().all()
