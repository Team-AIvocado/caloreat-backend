from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.user import User
from app.db.schemas.user import UserCreate, UserUpdate
from typing import Optional , List

class UserCrud:
    #결과가 1개면 객체 반환, 없으면 none
    #get_id
    #commit 은 enigne에서 일괄관리 + rollback까지
    # crud에선 flush()까지 관리
    @staticmethod
    async def get_id(db:AsyncSession, user_id:int) -> User | None:
        result=await db.execute(select(User).filter(User.user_id == user_id))
        return result.scalar_one_or_none()    
    
    async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    #유저네임으로 유저 조회
    async def get_user_by_username(db: AsyncSession, user_name:str) -> User | None:
        result = await db.execute(select(User).where(User.username == user_name))
        return result.scalar_one_or_none()

    #생성
    # async def create_user(db: AsyncSession, username: str, email: str, hashed_password: str) -> User:
    #     user = User(username=username, email=email, password=hashed_password)
    #     db.add(user)
    #     await db.flush()
    #     await db.refresh(user)
    #     return user
    @staticmethod
    async def create_user(db:AsyncSession, user:UserCreate) -> User :
        db_user=User(**user.model_dump())
        db.add(db_user)
        await db.flush()
        return db_user
    
    #삭제
    @staticmethod
    async def delete_by_id(db:AsyncSession, user_id:int):
        db_user=await db.get(User, user_id)
        if db_user:
            await db.delete(db_user)
            await db.flush() #db에 바로반영/ 롤백가능
            return db_user
        return None

    
    #username값 얻어오기(이름같은것만 필터링해서)
    @staticmethod
    async def get_username(db:AsyncSession, username:str):
        result=await db.execute(select(User).filter(User.username == username))
        return result.scalar_one_or_none()
    
    #email 값 얻어오기(이메일같으거 필터링)
    @staticmethod
    async def get_email(db:AsyncSession, email:str):
        result=await db.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none()
    
    #수정
    @staticmethod
    async def update_by_id(db:AsyncSession, user_id:int, user:UserUpdate):
        db_user=await db.get(User, user_id)
        if db_user:
            #patch(요청에서 전달된 필드만 업데이트하겠다) {"email":"aa@naver.com"}
            update_user=user.model_dump(exclude_unset=True)
            for i, j in update_user.items():
                setattr(db_user, i, j)  #update
            await db.flush()
            return db_user
        return None    


    #refresh token
    #user_id로 사용자 조회해서 존재하면 refresh_token필드 갱신하겠다
    @staticmethod
    async def update_refresh_token_id(
        db: AsyncSession, user_id: int, refresh_token: str
    ):
        db_user = await db.get(User, user_id)
        if db_user:
            db_user.refresh_token = refresh_token
            await db.flush()
        return db_user
    
    #######################
    # class UserCrud:
    # #get user_id 
    # @staticmethod
    # async def get_id( user_id:int, db:AsyncSession):    
    #     result = await db.execute(select(User).where(User.user_id == user_id))
    #     return result.scalar_one_or_none()   


    # #Create 
    # @staticmethod
    # async def create_user(user:UserCreate,db:AsyncSession)->User:
    #     db_user = User(**user.model_dump())
    #     db.add(db_user)
    #     await db.commit()     #commit/ flush 
    #     await db.refresh(db_user)    
    #     return db_user
    
    # #Delete 
    # @staticmethod
    # async def delete_user_by_id(user_id:int,db:AsyncSession):
    #     db_user = await db.get(User, user_id)
    #     if db_user:
    #         await db.delete(db_user)
    #         await db.commit()
    #         return db_user
    #     return None     

    # #Update (user_id)
    # @staticmethod
    # async def update_user_by_id(user:UserUpdate, user_id:int, db:AsyncSession):
    #     db_user = await db.get(User, user_id)
    #     if db_user:
    #         update_user = user.model_dump(exclude_unset=True)
    #         for name, value in update_user.items():
    #             #업데이트시 비밀번호 노출방지
    #             if name =="password":
    #                 value = await hash_password(value)
    #             setattr(db_user,name,value)
    #         await db.commit()     #commit/ flush 
    #         await db.refresh(db_user)             
    #         return db_user
    #     return None

    # #jwt 인증관련
    # #refresh_token
    # @staticmethod
    # async def update_refresh_token(
    #     user_id:int,refresh_token:str, db:AsyncSession) ->User:
    #     db_user = await db.get(User, user_id)        
    #     if db_user:
    #         db_user.refresh_token = refresh_token
    #         await db.flush()
    #     return db_user