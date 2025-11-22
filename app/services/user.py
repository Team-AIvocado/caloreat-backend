from fastapi import HTTPException, status
from app.db.schemas.user import UserCreate, UserUpdate
from app.core.jwt_context import get_pwd_hash

# from app.core.security import hash_password # security.py 파일 만든뒤 활성화
from app.db.models.user import User
from app.db.crud.user import UserCrud


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

# from app.core.jwt_context import get_pwd_hash

from datetime import datetime


# Service = Business Logic


class UserService:
    # 회원가입 (비밀번호 해시 후 저장)

    # create
    @staticmethod
    async def register_user(db: AsyncSession, email: str, username: str, password: str):
        # 중복 이메일 체크
        existing_email = await UserCrud.get_user_by_email(db, email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 사용중인 이메일입니다",
            )

        # 중복 username 체크
        existing_username = await UserCrud.get_user_by_username(db, username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 사용중인 이름입니다",
            )

        # password hasing
        hashed_pw = get_pwd_hash(password)
        user_create = UserCreate(email=email, username=username, password=hashed_pw)

        return await UserCrud.create_user(db, user_create)

    # read user by id
    @staticmethod
    async def get_user(db: AsyncSession, email: str):
        user = await UserCrud.get_user_by_id(db, email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User Not Found"
            )
        return user

    # read userlist (관리자)
    @staticmethod
    async def read_all_user(db: AsyncSession):
        users = await UserCrud.get_all_user(db)
        return users

    # update
    @staticmethod
    async def update_user(db: AsyncSession, user_id: int, user_data: UserUpdate):
        hashed_password = None
        if user_data.password:
            hashed_password = user_data.password
            # hashed_password = hash_password(user_data.password)

        # 확인필요
        updated_user = await UserCrud.update_user_by_id(
            db,
            user_id=user_id,
            user_name=user_data.username,
            email=user_data.email,
            password=hashed_password,
        )

        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not Found",
            )

        return updated_user

    # delete
    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int):
        is_deleted = await UserCrud.delete_user_by_id(db, user_id)
        if not is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found.",
            )
        return {"message": "User deleted successfully"}
