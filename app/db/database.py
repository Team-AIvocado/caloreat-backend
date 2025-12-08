from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.settings import settings

# 비동기엔진
async_engine = create_async_engine(settings.database_url, echo=False)

# 비동기엔진 세션연결
AsyncSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession
)
# 동기 엔진 (필요시)

# Base
Base = declarative_base()


# get_db
# transaction: update/ delete db이상(삽,삭,갱)발생, commit은 service에서 개별관리
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            # 엔진 commit()삭제
        except Exception:
            await session.rollback()  # 최종 안전장치 : pending중인 DB 작업취소
            raise  # 오류 발생 표시
        # finally:
        #     await session.close()     #코드 재활용성 : with 없을때


# DB연결 경로 확인 (dev) -삭제예정
print("DB URL:", settings.database_url)


# middleware 추가여부 (refresh_token rotation)
