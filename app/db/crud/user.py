from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.user import User
from app.db.schemas.user import UserCreate, UserUpdate
from typing import Optional, List


# CRUD = query
class UserCrud:

    # commit 은 enigne에서 일괄관리 + rollback까지
    # crud에선 flush()까지 관리

    # create
    @staticmethod
    async def create_user(db: AsyncSession, user: UserCreate) -> User:
        db_user = User(**user.model_dump())
        db.add(db_user)
        await db.flush()  # PK생성, DB내 query insert
        await db.refresh(db_user)  # 새로입력된값을 다시 반환위해
        return db_user
        # refresh는 SELECT를 다시 쏘는 비용이 들어간다 → 오버헤드발생

    # read (helpers)  - read는 쿼리담당 함수만 : 'get'
    # id: 조회
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
        result = await db.execute(select(User).filter(User.id == user_id))
        return result.scalar_one_or_none()

    # none 으로 service에 반환하고 service에서 예외발생 시킴(+err msg)

    # username: 조회
    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
        result = await db.execute(select(User).filter(User.username == username))
        return result.scalar_one_or_none()

    # email: 조회
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none()

    # 모든유저 조회
    @staticmethod
    async def get_all_user(db: AsyncSession) -> List[User]:
        result = await db.execute(select(User))
        return result.scalars().all()

    # update (회원정보수정) : setattr + exclude_unset=True
    @staticmethod
    async def update_user_by_id(
        db: AsyncSession, user_id: int, user: UserUpdate
    ) -> User | None:
        db_user = await db.get(User, user_id)
        if db_user:
            # patch(요청에서 전달된 필드만 업데이트하겠다) {"email":"aa@naver.com"}
            update_user = user.model_dump(exclude_unset=True)
            for i, j in update_user.items():
                setattr(db_user, i, j)  # orm 객체수정됨
            await db.flush()  # sql업데이트 반영
            return db_user
        return None

    # delete (회원탈퇴(삭제))
    @staticmethod
    async def delete_user_by_id(db: AsyncSession, user_id: int):
        db_user = await db.get(User, user_id)
        if db_user:
            await db.delete(db_user)
            await db.flush()  # db에 바로반영/ 롤백가능
            return db_user
        return None

    # 회원가입 추가기능
    # is_exist 중복

    # login
    # logout

    # #jwt 인증 / oauth2는 router단에서 적용
    # #refresh_token
    # @staticmethod
    # async def update_refresh_token(
    #     user_id:int,refresh_token:str, db:AsyncSession) ->User:
    #     db_user = await db.get(User, user_id)
    #     if db_user:
    #         db_user.refresh_token = refresh_token
    #         await db.flush()
    #     return db_user
