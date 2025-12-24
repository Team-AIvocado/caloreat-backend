from fastapi import APIRouter, Depends, HTTPException, status, Response, Request

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.auth import get_current_user, get_user_id, get_current_user_optional
from app.db.schemas.user import (
    UserRead,
    UserCreate,
    UserUpdate,
    UserDetailRead,
    UserLogin,
    LoginResponse,
    LogoutResponse,
    PasswordUpdate,
    MessageResponse,
)
from app.db.database import get_db
from app.db.models.user import User
from app.services.user import UserService
from app.db.crud.user import UserCrud

from app.core.auth import set_login_cookies, set_access_cookie

from typing import Annotated

router = APIRouter(prefix="/users", tags=["User"])

# 최대한 restful api설계방식


@router.get("/checkemail", response_model=MessageResponse)
async def checkemail(email: str, db: AsyncSession = Depends(get_db)) -> MessageResponse:
    existing_email = await UserCrud.get_user_by_email(db, email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 사용중인 이메일입니다",
        )
    return {"message": "사용 가능한 이메일입니다"}


@router.get("/checkid", response_model=MessageResponse)
async def checkid(id: str, db: AsyncSession = Depends(get_db)) -> MessageResponse:
    existing_id = await UserCrud.get_user_by_username(db, id)
    if existing_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 사용중인 아이디입니다",
        )
    return {"message": "사용 가능한 아이디입니다"}


# 회원가입 - JWT 로그인 - /me 인증확인 - 수정 - 삭제 - 중복체크
# signup
@router.post("/signup", response_model=UserRead)
async def signup(user: UserCreate, db: AsyncSession = Depends(get_db)) -> User:
    db_user = await UserService.register_user(
        db, user.email, user.username, user.password, user.nickname
    )
    return db_user


# login (유저정보만 클라이언트로 반환) #관리자폐이지 추가고려시 (admin uid:1, 모든권한 슈퍼계정)
@router.post("/login", response_model=LoginResponse)
async def login(
    user: UserLogin, response: Response, db: AsyncSession = Depends(get_db)
):  # response fastapi가 자동으로 dependency 주입
    result = await UserService.login(db, user)
    db_user, access_token, refresh_token = result
    set_login_cookies(
        response, access_token, refresh_token
    )  # token은 body x 쿠키로 관리(localstorage 필요 x)/ CSRF 취약점 존재
    return db_user


# 인증 상태 확인 (401 대신 null 반환 - 프론트엔드 초기 로딩용)
@router.get("/me/check", response_model=UserRead | None, summary="인증 상태 확인")
async def check_auth(current_user=Depends(get_current_user_optional)):
    return current_user


# 사용자 조회 (현재로그인된 사용자 본인 정보조회)
# get_current_user 의존성 주입
@router.get("/me", response_model=UserRead, summary="내정보 조회")
async def read_me(current_user=Depends(get_current_user)):
    return current_user


# current_user-> 쿠키상태유지

# # 모든 사용자조회(관리자용)  : is_admin or username==admin 필요하면 추가
# # service logic 생성필요
# @router.get("/", response_model=list[UserRead])
# async def read_all_user_route(db: AsyncSession, current_user= ):
#     users = await read_all_user(db)
#     return users


# user update (로그인된 id만 수정가능) endpoint -> /me로 통일(정적세그먼트)
# /{user_id}임의접근 x -> /me 본인정보만
@router.patch("/me", response_model=UserRead, summary="내정보 수정")
async def update_user_by_id(
    user: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_user_id),  # 현재로그인된 본인정보
):
    result = await UserService.update_user(db, current_user_id, user)
    return result


# 비밀번호 변경
@router.patch("/me/password", description="비밀번호변경")
async def change_my_pw(
    pw_data: PasswordUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    await UserService.update_pw(db, current_user, pw_data)
    return {"msg": "비밀번호 변경 완료"}


# delete_user 개인 회원탈퇴  // 프론트 bool값
# current_user_id 반환 // 추후 soft delete 추가 고려
# delete response schema 추가 고려
@router.delete("/me", summary="개인회원 탈퇴")
async def delete_me(
    current_user_id: int = Depends(get_user_id), db: AsyncSession = Depends(get_db)
):
    await UserService.delete_user(db, current_user_id)
    return {"deleted": True, "deleted_user_id": current_user_id}


# # delete_user 관리자용
# @router.delete("/delete/{user_id}")
# async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
#     result = await UserCrud.delete_user_by_id(user_id, db)
#     return {"msg": "회원삭제", "deleted": result}


# logout
@router.post("/logout")
async def logout(request: Request, response: Response):
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return {"success": True}


# refresh (access_token 만료 후 재발급) / a
@router.post("/refreshAccess")
async def refresh(request: Request, response: Response):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(401, "refresh token 없음")

    new_access_token = await UserService.refresh(refresh_token)
    set_access_cookie(response, new_access_token)

    return {"msg": "새 토큰 발급 완료"}
