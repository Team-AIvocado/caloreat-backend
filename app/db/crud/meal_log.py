from sqlalchemy.ext.asyncio import AsyncSession
from app.db.schemas.meal_log import MealLogCreate
from app.db.models.meal_log import MealLog
from app.db.models.meal_item import MealItem


class MealLogCrud:
    @staticmethod
    async def create_meal_log_db(
        db: AsyncSession, meal_create: MealLogCreate, current_user_id: int
    ) -> MealLog:
        """
        MealLog와 MealItem을 DB에 생성
        """
        #  create ai server간 파이프라인 쪽 생성로직
        # 1. MealLog 객체 생성 (부모)
        # - MealLog 모델 인스턴스화
        # - user_id, meal_type, eaten_at, image_urls 등 매핑
        # - db.add() 호출

        # 2. ID 생성을 위한 Flush
        # - await db.flush() 및 refresh() 호출하여 new_log.id 확보

        # 3. MealItem 리스트 저장 (자식)
        # - meal_create.meal_items 반복 순회
        # - 각 아이템에 대해 MealItem 모델 인스턴스화
        # - meal_log_id에 위에서 확보한 new_log.id 할당
        # - nutritions 필드 매핑
        # - db.add() 호출

        # 4. MealLog 반환
        # - (commit은 Service 레이어에서 담당하므로 여기선 하지 않음)
        # - return new_log
        pass

    @staticmethod
    async def get_meal_log_db(db: AsyncSession, user_id: int, date) -> list[MealLog]:
        """
        특정 날짜의 식단 기록 조회
        """
        # 1. 쿼리 작성 (select)
        # - MealLog 모델 조회
        # - 조건: user_id 일치 AND eaten_at 날짜 일치
        # - 옵션: .options(selectinload(MealLog.meal_items))로 자식 데이터 함께 로드 권장

        # 2. 실행 및 반환
        # - result = await db.execute(query)
        # - return result.scalars().all()
        pass

    @staticmethod
    async def update_meal_log_db(
        db: AsyncSession, meal_log_id: int, user_id: int, update_data: dict
    ):
        """
        식단 기록 수정 (통교체 or 일부수정)
        """
        # 1. 대상 조회
        # - meal_log_id와 user_id로 검증 (내 식단만 수정 가능)

        # 2. 데이터 업데이트
        # - update_data의 필드값으로 MealLog 속성 변경
        # - 만약 MealItem도 수정된다면? -> 기존 아이템 삭제 후 재생성 전략 or 개별 수정 전략 선택

        # 3. flush/commit (Service 레이어 위임 가능)
        pass

    @staticmethod
    async def delete_meal_log_db(db: AsyncSession, meal_log_id: int, user_id: int):
        """
        식단 기록 삭제
        """
        # 1. 대상 조회
        # - meal_log_id와 user_id로 검증

        # 2. 삭제 실행
        # - db.delete(meal_log)
        # - cascade 설정이 되어있다면 자식(MealItem)도 자동 삭제됨
        pass
