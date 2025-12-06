from fastapi import HTTPException, status
from app.db.schemas.user import UserCreate, UserUpdate, UserLogin
from app.core.jwt_context import (
    get_pwd_hash,
    verify_pwd,
    create_access_token,
    create_refresh_token,
    verify_token,
    verify_refresh_token,
)

# from app.core.security import hash_password # security.py 파일 만든뒤 활성화
from app.db.models.user import User
from app.db.crud.user import UserCrud
from app.db.schemas.user import (
    PasswordUpdate,
)  # TODO: 왜 routers로 연결됐는데 정상작동됐는지 체크필요

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

# from app.core.jwt_context import get_pwd_hash

from datetime import datetime


# Service = Business Logic / db transaction 관리(commit/rollback/refresh)


class UserService:
    # 회원가입 (비밀번호 해시 후 저장)

    # create
    @staticmethod
    async def register_user(
        db: AsyncSession, email: str, username: str, password: str, nickname: str
    ):
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

        # TODO : 닉네임 중복처리는 나중에..

        # password hasing
        hashed_pw = get_pwd_hash(password)  # nickname입력안하면 username
        user_create = UserCreate(
            email=email,
            username=username,
            password=hashed_pw,
            nickname=nickname or username,
        )

        # commit / rollback transaction 개별관리
        try:
            db_user = await UserCrud.create_user(db, user_create)
            await db.commit()
            await db.refresh(db_user)  #
            return db_user

        except Exception:
            await db.rollback()
            raise

    # read user by id
    # id기준으로 사용자 프로필조회 ≠ 이메일기준으로 로그인전용 함수
    @staticmethod
    async def get_user(db: AsyncSession, user_id: str):
        user = await UserCrud.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User Not Found"
            )
        return user

    # # read userlist (관리자)
    # @staticmethod
    # async def read_all_user(db: AsyncSession):
    #     users = await UserCrud.get_all_user(db)
    #     return users

    # update (updated_at 추가 고려)
    @staticmethod
    async def update_user(db: AsyncSession, current_user_id: int, user: UserUpdate):
        # db 유효성 검사
        db_user = await UserCrud.get_user_by_id(db, current_user_id)
        if not db_user:
            raise HTTPException(404, "Not found")

        # patch(요청에서 전달된 필드만 업데이트)
        update_user = user.model_dump(exclude_unset=True)

        # http 500 err 예외처리
        # 중복 이메일 체크(본인제외) (db예외 터지기전 비지니스로직위반 차단)
        # update_user는 dict 이므로 keyname으로 조건분기, obj chain x (user.email)
        # obj형태 chaining 불가 -> dict로 변경여부 체크해야함
        if "email" in update_user:
            existing = await UserCrud.get_user_by_email(db, update_user["email"])
            if existing and existing.id != current_user_id:
                raise HTTPException(400, "이미 사용중인 이메일입니다")

        # username = login_id : immutable 예외처리없이 응답필드 삭제예정 우선 기능동작확인만

        # 비밀번호변경 별도 엔드포인트로 분리

        # db이상현상 방지 예외처리
        try:
            updated_user = await UserCrud.update_user(db, db_user, update_user)

            if not updated_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"존재하지 않는 유저",
                )

            # db쓰기 확정 / refresh
            await db.commit()
            await db.refresh(updated_user)
            return updated_user

        except Exception:
            await db.rollback()
            raise

    # update pw : 보안문제 생각 + 편의성
    @staticmethod
    async def update_pw(db: AsyncSession, current_user, pw_data: PasswordUpdate):

        # 비밀번호 변경 권한검증(본인인지 old_pw기준으로)
        if not verify_pwd(pw_data.old_password, current_user.password):
            raise HTTPException(400, "old pw incorrect")

        # 새 비밀번호 hash
        new_pw_hashed = get_pwd_hash(pw_data.new_password)

        current_user.password = new_pw_hashed

        # db반영
        await db.commit()
        await db.refresh(current_user)

        return None

    # delete
    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int) -> bool:
        try:
            is_deleted = await UserCrud.delete_user_by_id(db, user_id)
            if not is_deleted:
                raise HTTPException(status_code=404, detail="없는 회원 입니다")
            
            await db.commit()
            return True

        except Exception:
            await db.rollback()
            raise

    # login
    @staticmethod
    async def login(db: AsyncSession, user: UserLogin) -> tuple:
        # username, email 둘다 허용위해 account 변수사용
        account = user.account

        # 이메일, 아이디 허용분기
        if "@" in account and "." in account:
            db_user = await UserCrud.get_user_by_email(db, account)  # login용 email조회
        else:
            db_user = await UserCrud.get_user_by_username(db, account)

        # 없는 아이디, 이메일
        if not db_user:
            raise HTTPException(
                status_code=400, detail="이메일 또는 아이디를 확인해주세요"
            )
        # 비밀번호 불일치 시
        if not verify_pwd(user.password, db_user.password):
            raise HTTPException(status_code=401, detail="비밀번호를 확인해주세요")

        # token
        access_token = create_access_token(db_user.id)
        refresh_token = create_refresh_token(db_user.id)

        return db_user, access_token, refresh_token

        # login
        # # refresh_token rotation 추가시 활성화(미들웨어사용 토큰 자동갱신)
        # updated_user = await UserCrud.update_refresh_token_id(
        #     db, db_user.user_id, refresh_token
        # )
        # await db.commit() 로그인과정에서 뭔가를DB에 변경 했을때만필요(refresh_token rotation)
        # await db.refresh(db_user)

    # refresh_token
    # (별도 endpoints용 ) -별도유지 or rotation 적용하면 삭제
    @staticmethod
    async def refresh(refresh_token: str):
        payload = verify_refresh_token(refresh_token)
        user_id = int(payload.get("sub"))
        new_access_token = create_access_token(user_id)
        return new_access_token
