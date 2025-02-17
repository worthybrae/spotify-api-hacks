from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator

# Update the URL to use async driver
SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/spotify_db"

# Create async engine
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,  # Set to False in production
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

# Async dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()