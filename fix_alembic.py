import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import os
from dotenv import load_dotenv

load_dotenv(".env")
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "postgresql+asyncpg://postgres:12345@localhost:5432/caloreat"


async def reset_alembic():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        print("Resetting alembic_version table...")
        await conn.execute(text("DROP TABLE IF EXISTS alembic_version"))
        await conn.execute(
            text(
                "CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL, PRIMARY KEY (version_num))"
            )
        )
        await conn.execute(
            text("INSERT INTO alembic_version (version_num) VALUES ('96da12e0d383')")
        )
        print("Reset complete. Current version: 96da12e0d383")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(reset_alembic())
