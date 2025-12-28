"""
OAuth 라우터

Google/Kakao 소셜 로그인 엔드포인트
"""

import secrets
from fastapi import APIRouter, Depends, HTTPException, Response, Cookie
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.database import get_db
from app.services.oauth import GoogleOAuthService, KakaoOAuthService
from app.core.auth import set_login_cookies
from app.core.settings import settings
from app.db.crud.user_profile import UserProfileCrud

router = APIRouter(prefix="/auth", tags=["OAuth"])

# State 쿠키 설정
STATE_COOKIE_NAME = "oauth_state"
STATE_COOKIE_MAX_AGE = 600  # 10분


@router.get("/google/login")
async def google_login(response: Response):
    """
    구글 로그인 시작

    프론트엔드에서 이 URL을 호출하면 구글 로그인 페이지 URL을 반환합니다.
    프론트에서 해당 URL로 리다이렉트하면 됩니다.
    state 파라미터를 생성하여 CSRF 공격을 방지합니다.
    """
    if not settings.google_client_id:
        raise HTTPException(status_code=500, detail="Google OAuth가 설정되지 않았습니다")

    # CSRF 방지용 state 생성
    state = secrets.token_urlsafe(32)

    # state를 쿠키에 저장
    response.set_cookie(
        key=STATE_COOKIE_NAME,
        value=state,
        httponly=True,
        secure=False,  # 프로덕션에서는 True
        samesite="Lax",
        max_age=STATE_COOKIE_MAX_AGE,
    )

    login_url = GoogleOAuthService.get_google_login_url(state)
    return {"url": login_url}


@router.get("/google/callback")
async def google_callback(
    code: Optional[str] = None,
    state: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    oauth_state: Optional[str] = Cookie(None),
):
    """
    구글 로그인 콜백

    구글에서 인증 완료 후 리다이렉트되는 엔드포인트입니다.
    1. state 검증 (CSRF 방지)
    2. code로 access_token 교환
    3. 유저 정보 조회
    4. DB에서 유저 조회/생성
    5. JWT 발급 후 쿠키에 저장
    6. 프론트엔드로 리다이렉트
    """
    try:
        # 필수 파라미터 검증 (동의 페이지에서 뒤로가기 등)
        if not code or not state:
            return RedirectResponse(url="http://localhost:5173/?error=oauth_failed", status_code=302)

        # 1. State 검증 (CSRF 방지)
        if not oauth_state or oauth_state != state:
            return RedirectResponse(url="http://localhost:5173/?error=oauth_failed", status_code=302)

        # 2. code로 Google access_token 교환
        token_data = await GoogleOAuthService.get_google_token(code)
        google_access_token = token_data.get("access_token")

        if not google_access_token:
            raise HTTPException(status_code=400, detail="구글 토큰 교환 실패")

        # 2. Google 유저 정보 조회
        google_user_info = await GoogleOAuthService.get_google_user_info(google_access_token)

        if not google_user_info.get("email"):
            raise HTTPException(status_code=400, detail="구글 유저 정보 조회 실패")

        # 3. 유저 인증 처리 (조회/생성 + JWT 발급)
        user, access_token, refresh_token = await GoogleOAuthService.authenticate_google_user(
            db, google_user_info
        )

        # 4. 사용자 프로필(신체정보) 존재 여부 확인
        user_profile = await UserProfileCrud.get_profile_db(db, user.id)

        # 5. DB 커밋
        await db.commit()

        # 6. 쿠키에 JWT 저장
        # 프로필 있으면 dashboard, 없으면 userinfo로 리다이렉트
        if user_profile:
            redirect_url = "http://localhost:5173/main/dashboard"
        else:
            redirect_url = "http://localhost:5173/userinfo"
        redirect_response = RedirectResponse(url=redirect_url, status_code=302)

        # state 쿠키 삭제
        redirect_response.delete_cookie(key=STATE_COOKIE_NAME)

        redirect_response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,  # 개발환경에서는 False, 프로덕션에서는 True
            samesite="Lax",
            max_age=int(settings.access_token_expire.total_seconds()),
        )
        redirect_response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite="Lax",
            max_age=int(settings.refresh_token_expire.total_seconds()),
        )

        return redirect_response

    except Exception as e:
        print(f"Google OAuth 에러: {e}")
        return RedirectResponse(url="http://localhost:5173/?error=oauth_failed", status_code=302)


@router.get("/kakao/login")
async def kakao_login(response: Response):
    """
    카카오 로그인 시작

    프론트엔드에서 이 URL을 호출하면 카카오 로그인 페이지 URL을 반환합니다.
    프론트에서 해당 URL로 리다이렉트하면 됩니다.
    state 파라미터를 생성하여 CSRF 공격을 방지합니다.
    """
    if not settings.kakao_client_id:
        raise HTTPException(status_code=500, detail="Kakao OAuth가 설정되지 않았습니다")

    # CSRF 방지용 state 생성
    state = secrets.token_urlsafe(32)

    # state를 쿠키에 저장
    response.set_cookie(
        key=STATE_COOKIE_NAME,
        value=state,
        httponly=True,
        secure=False,  # 프로덕션에서는 True
        samesite="Lax",
        max_age=STATE_COOKIE_MAX_AGE,
    )

    login_url = KakaoOAuthService.get_kakao_login_url(state)
    return {"url": login_url}


@router.get("/kakao/callback")
async def kakao_callback(
    code: Optional[str] = None,
    state: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    oauth_state: Optional[str] = Cookie(None),
):
    """
    카카오 로그인 콜백

    카카오에서 인증 완료 후 리다이렉트되는 엔드포인트입니다.
    1. state 검증 (CSRF 방지)
    2. code로 access_token 교환
    3. 유저 정보 조회
    4. DB에서 유저 조회/생성
    5. JWT 발급 후 쿠키에 저장
    6. 프론트엔드로 리다이렉트
    """
    try:
        # 필수 파라미터 검증 (동의 페이지에서 뒤로가기 등)
        if not code or not state:
            return RedirectResponse(url="http://localhost:5173/?error=oauth_failed", status_code=302)

        # 1. State 검증 (CSRF 방지)
        if not oauth_state or oauth_state != state:
            return RedirectResponse(url="http://localhost:5173/?error=oauth_failed", status_code=302)

        # 2. code로 Kakao access_token 교환
        token_data = await KakaoOAuthService.get_kakao_token(code)
        kakao_access_token = token_data.get("access_token")

        if not kakao_access_token:
            raise HTTPException(status_code=400, detail="카카오 토큰 교환 실패")

        # 2. Kakao 유저 정보 조회
        kakao_user_info = await KakaoOAuthService.get_kakao_user_info(kakao_access_token)

        if not kakao_user_info.get("id"):
            raise HTTPException(status_code=400, detail="카카오 유저 정보 조회 실패")

        # 3. 유저 인증 처리 (조회/생성 + JWT 발급)
        user, access_token, refresh_token = await KakaoOAuthService.authenticate_kakao_user(
            db, kakao_user_info
        )

        # 4. 사용자 프로필(신체정보) 존재 여부 확인
        user_profile = await UserProfileCrud.get_profile_db(db, user.id)

        # 5. DB 커밋
        await db.commit()

        # 6. 쿠키에 JWT 저장
        # 프로필 있으면 dashboard, 없으면 userinfo로 리다이렉트
        if user_profile:
            redirect_url = "http://localhost:5173/main/dashboard"
        else:
            redirect_url = "http://localhost:5173/userinfo"
        redirect_response = RedirectResponse(url=redirect_url, status_code=302)

        # state 쿠키 삭제
        redirect_response.delete_cookie(key=STATE_COOKIE_NAME)

        redirect_response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,
            samesite="Lax",
            max_age=int(settings.access_token_expire.total_seconds()),
        )
        redirect_response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite="Lax",
            max_age=int(settings.refresh_token_expire.total_seconds()),
        )

        return redirect_response

    except Exception as e:
        print(f"Kakao OAuth 에러: {e}")
        return RedirectResponse(url="http://localhost:5173/?error=oauth_failed", status_code=302)
