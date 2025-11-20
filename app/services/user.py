from fastapi import HTTPException, status
from app.db.schemas.user import UserCreate, UserUpdate
# from app.core.security import hash_password # security.py 파일 만든뒤 활성화
from app.db.models.user import User
from app.db.crud.user import UserCrud
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.jwt_context import get_pwd_hash
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status


from datetime import datetime
from app.db.crud import user as user_crud



class UserService:
    # email로 유저 조회
    async def get_user_by_email(db: AsyncSession, email: str):
        return await db.scalar(select(User).where(User.email == email)) 
        # scalar(select(...)) -> 결과 중 첫 번째(row 1개)를 가져오는 SQLAlchemy 방식
        # DB : SELECT * FROM users WHERE email=:email LIMIT 1

    # id(PK)로 유저 조회
    async def get_user_by_id(db: AsyncSession, id: int):
        return db.get(User, id)
        # db.get(Model, pk) -> pk기반 조회(가장 빠르고 기본적인 조회 방식)

    # 회원가입 (비밀번호 해시 후 저장)
    # create user
    async def register_user(db: AsyncSession, username: str, email: str, password: str):
    # 중복 이메일 체크
        existing_email = await UserCrud.get_user_by_email(db, email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # 중복 username 체크
        existing_username = await UserCrud.get_user_by_username(db, username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        

        # hashed_pw = get_pwd_hash(password)
        hashed_pw = get_pwd_hash(password)
        return await UserCrud.create_user(db, username=username, email=email, password=hashed_pw)






    # # 회원정보 수정 (PATCH 방식)
    # async def update_user(db: AsyncSession, db_user: User, user_in: UserUpdate):
    #     update_data = user_in.model_dump(exclude_unset=True)
    #     # exclude_unset=True -> 사용자가 보낸 값만 추출 (부분 수정 가능)

    #     for key, value in update_data.items():
    #         setattr(db_user, key, value)

    #     db.commit()         # 변경내용을 DB에 반영
    #     db.refresh(db_user) # 갱신된 객체 다시 읽어오기 (DB 최신 상태)
    #     return db_user

    # # 회원 삭제
    # async def delete_user(db: AsyncSession, db_user: User):
    #     db.delete(db_user)  # 세션에서 해당 객체 삭제 처리
    #     db.commit()         # DB에서 실제 삭제 실행



