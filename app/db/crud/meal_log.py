from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.meal_log import MealLog
from app.db.models.meal_item import MealItem


class MealLogCrud:
    """
    MealLog 및 MealItem에 대한 순수 DB CRUD 작업을 담당합니다.
    **kwargs 언패킹을 사용하여 딕셔너리 기반으로 모델을 생성합니다.
    """

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

        return new_items
