from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.user import User
from app.db.schemas.user import UserCreate, UserUpdate
from typing import Optional
from fastapi import HTTPException


# CRUD = query
class UserCrud:
    # crud 에선 db query만 관리
    # commit, refresh, rollback 은 service에서 개별관리
    # crud에선 add(), flush()까지 관리

    # create
    @staticmethod
    async def create_user(db: AsyncSession, user: UserCreate) -> User:
        db_user = User(**user.model_dump())
        db.add(db_user)
        await db.flush()  # PK생성, DB내 query insert
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
    async def get_all_user(db: AsyncSession) -> list[User]:
        result = await db.execute(select(User))
        return result.scalars().all()

    # update (회원정보수정) : setattr + exclude_unset=True
    @staticmethod
    async def update_user(db: AsyncSession, db_user, update_user: dict) -> User | None:
        for i, j in update_user.items():
            setattr(db_user, i, j)  # orm 객체수정, Orm state-> dirty
        await db.flush()  # sql문 쿼리생성, data 업데이트
        return db_user

    # delete (회원탈퇴(삭제))
    # 트랜잭션고려 예외처리먼저- 구조변경
    @staticmethod
    async def delete_user_by_id(db: AsyncSession, user_id: int) -> bool:
        db_user = await db.get(User, user_id)
        # 실패시 조기종료
        if not db_user:
            return False

        await db.delete(db_user)
        await db.flush()  # db에 쿼리문날림/ 롤백가능
        return True

    # 회원가입 추가기능
    # is_exist 중복

    # login

    # #refresh_token    #TODO: rotation 자동갱신적용 vs front intercept
    # async def update_refresh_token(
    #     user_id:int,refresh_token:str, db:AsyncSession) ->User:
    #     db_user = await db.get(User, user_id)
    #     if db_user:
    #         db_user.refresh_token = refresh_token
    #         await db.flush()
    #     return db_user
