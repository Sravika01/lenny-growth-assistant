from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import text

from app.config import settings
from app.models.db_models import Base


engine = create_async_engine(
    settings.database_url,
    echo=True,
)


AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def test_database_connection():
    async with engine.begin() as connection:
        await connection.execute(text("SELECT 1"))


async def create_tables():
    async with engine.begin() as connection:

        # Enable pgvector extension
        await connection.execute(
            text("CREATE EXTENSION IF NOT EXISTS vector")
        )

        # Create all application tables
        await connection.run_sync(
            Base.metadata.create_all
        )