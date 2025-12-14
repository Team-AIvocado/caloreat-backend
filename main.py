from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from fastapi import FastAPI, APIRouter
from app.db.database import Base, async_engine
from app.db import models
from app.core.settings import settings
from app.routers import router as all_routes

# lifespan
from contextlib import asynccontextmanager

# env load
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")


# lifespan
# 현재구조는 alembic과 충돌구조 - 개발편의성
# lifespan != migration(alembic)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run Alembic migrations at startup
    import subprocess

    try:
        print("Running Alembic migrations...")
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        print("Alembic migrations completed.")
    except Exception as e:
        print(f"Error running Alembic migrations: {e}")

    yield
    await async_engine.dispose()  # DB 연결 종료


print("SECRET_KEY:", settings.secret_key)
app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"message": "Welcome to Caloreat API", "status": "ok"}


# 배포시 서버가 제대로 살아있나 체크하는 엔드포인트.
@app.get("/health")
def health_check():
    return {"status": "ok"}


# 미들웨어 등록 (front:intercept, 토큰보안 안정성)
# 허용할 출처 목록
import os

origins = os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:5173,https://caloreat-ten.vercel.app,null"
).split(",")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["*"],  #모든 도메인요청 허용
    allow_origins=origins,
    allow_credentials=True,  # 자격증명 true일경우에만 응답 노출
    allow_methods=[
        "*"
    ],  # 모든 http메소드 허용 # 소셜인증 사용시 https만 혀용필요할수도있음
    allow_headers=["*"],
)

# 라우터 등록
# v1 운영버전
api_v1 = APIRouter(prefix="/api/v1")
api_v1.include_router(all_routes)
app.include_router(api_v1)

# #v2 운영버전 - 호환성깨지면 v2폴더 생성(router~crud)
# api_v2 = APIRouter(prefix="/api/v2")
# api_v2.include_router(all_routes)
# app.include_router(api_v2)


# # for check
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
