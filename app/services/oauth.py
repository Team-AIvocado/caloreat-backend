"""
OAuth 서비스

Google/Kakao OAuth 2.0 흐름:
1. 프론트에서 /auth/{provider}/login 호출 → 로그인 페이지 URL 반환
2. 유저가 로그인 완료 → 콜백 URL로 리다이렉트 (code 포함)
3. /auth/{provider}/callback에서 code로 access_token 교환
4. access_token으로 유저 정보 조회
5. DB에서 유저 조회/생성 → JWT 발급
"""

import httpx
from urllib.parse import urlencode
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import settings
from app.db.crud.user import UserCrud
from app.db.models.user import User
from app.core.jwt_context import create_access_token, create_refresh_token


# Google OAuth 상수
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


class GoogleOAuthService:
    """Google OAuth 서비스"""

    @staticmethod
    def get_google_login_url(state: str) -> str:
        """
        구글 로그인 페이지 URL 생성

        Args:
            state: CSRF 방지용 랜덤 state 값

        Returns:
            구글 OAuth 로그인 URL
        """
        params = {
            "client_id": settings.google_client_id,
            "redirect_uri": settings.google_redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
        }
        return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"

    @staticmethod
    async def get_google_token(code: str) -> dict:
        """
        Authorization code로 Google access_token 교환

        Args:
            code: 구글에서 받은 authorization code

        Returns:
            {"access_token": str, "id_token": str, ...}
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": settings.google_redirect_uri,
                },
            )
            response.raise_for_status()
            return response.json()

    @staticmethod
    async def get_google_user_info(access_token: str) -> dict:
        """
        Google access_token으로 유저 정보 조회

        Args:
            access_token: 구글 access_token

        Returns:
            {"id": str, "email": str, "name": str, "picture": str, ...}
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            return response.json()

    @staticmethod
    async def authenticate_google_user(
        db: AsyncSession, google_user_info: dict
    ) -> tuple[User, str, str]:
        """
        구글 유저 정보로 인증 처리 (유저 조회/생성 + JWT 발급)

        Args:
            db: DB 세션
            google_user_info: 구글 유저 정보

        Returns:
            (User, access_token, refresh_token)
        """
        email = google_user_info.get("email")
        google_id = google_user_info.get("id")
        name = google_user_info.get("name", "")

        # 1. 이메일로 기존 유저 조회
        user = await UserCrud.get_user_by_email(db, email)

        if user:
            # 기존 유저가 local 계정이면 google로 업데이트 (또는 에러 처리)
            if user.provider == "local":
                # 이미 이메일/비밀번호로 가입한 유저 - 연동 처리
                user.provider = "google"
                await db.flush()
        else:
            # 2. 새 유저 생성
            user = User(
                email=email,
                username=f"google_{google_id}",  # 구글 ID 기반 유니크 username
                password=None,  # 소셜 로그인은 비밀번호 없음
                nickname=name,
                provider="google",
                email_verified=True,  # 구글 인증된 이메일
            )
            db.add(user)
            await db.flush()
            await db.refresh(user)

        # 3. JWT 토큰 발급
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        # commit은 라우터에서 처리 (프로필 조회 후)
        return user, access_token, refresh_token


# Kakao OAuth 상수
KAKAO_AUTH_URL = "https://kauth.kakao.com/oauth/authorize"
KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
KAKAO_USERINFO_URL = "https://kapi.kakao.com/v2/user/me"


class KakaoOAuthService:
    """Kakao OAuth 서비스"""

    @staticmethod
    def get_kakao_login_url(state: str) -> str:
        """
        카카오 로그인 페이지 URL 생성

        Args:
            state: CSRF 방지용 랜덤 state 값

        Returns:
            카카오 OAuth 로그인 URL
        """
        params = {
            "client_id": settings.kakao_client_id,
            "redirect_uri": settings.kakao_redirect_uri,
            "response_type": "code",
            "state": state,
        }
        return f"{KAKAO_AUTH_URL}?{urlencode(params)}"

    @staticmethod
    async def get_kakao_token(code: str) -> dict:
        """
        Authorization code로 Kakao access_token 교환

        Args:
            code: 카카오에서 받은 authorization code

        Returns:
            {"access_token": str, "refresh_token": str, ...}
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                KAKAO_TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "client_id": settings.kakao_client_id,
                    "client_secret": settings.kakao_client_secret,
                    "redirect_uri": settings.kakao_redirect_uri,
                    "code": code,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
            return response.json()

    @staticmethod
    async def get_kakao_user_info(access_token: str) -> dict:
        """
        Kakao access_token으로 유저 정보 조회

        Args:
            access_token: 카카오 access_token

        Returns:
            {"id": int, "kakao_account": {"email": str, "profile": {"nickname": str}}, ...}
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                KAKAO_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            return response.json()

    @staticmethod
    async def authenticate_kakao_user(
        db: AsyncSession, kakao_user_info: dict
    ) -> tuple[User, str, str]:
        """
        카카오 유저 정보로 인증 처리 (유저 조회/생성 + JWT 발급)

        Args:
            db: DB 세션
            kakao_user_info: 카카오 유저 정보

        Returns:
            (User, access_token, refresh_token)
        """
        kakao_id = kakao_user_info.get("id")
        kakao_account = kakao_user_info.get("kakao_account", {})
        email = kakao_account.get("email")
        profile = kakao_account.get("profile", {})
        nickname = profile.get("nickname", "")

        # 이메일이 없는 경우 카카오 ID 기반 이메일 생성
        if not email:
            email = f"kakao_{kakao_id}@kakao.local"

        # 1. 이메일로 기존 유저 조회
        user = await UserCrud.get_user_by_email(db, email)

        if user:
            # 기존 유저가 local 계정이면 kakao로 업데이트
            if user.provider == "local":
                user.provider = "kakao"
                await db.flush()
        else:
            # 2. 새 유저 생성
            user = User(
                email=email,
                username=f"kakao_{kakao_id}",
                password=None,
                nickname=nickname or f"카카오유저{str(kakao_id)[-4:]}",
                provider="kakao",
                email_verified=True,
            )
            db.add(user)
            await db.flush()
            await db.refresh(user)

        # 3. JWT 토큰 발급
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        # commit은 라우터에서 처리 (프로필 조회 후)
        return user, access_token, refresh_token
