# tests/conftest.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, Integer, JSON

# Create a separate test base
TestBase = declarative_base()

# Use a different table name for testing
class TestArtist(TestBase):
    __tablename__ = "test_artists"  # Changed from "artists" to "test_artists"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    genres = Column(JSON)  # Using JSON instead of ARRAY for SQLite
    popularity = Column(Integer)

@pytest.fixture(scope="function")
async def test_engine():
    engine = create_async_engine(
        "sqlite+aiosqlite:///./test_spotify.db",
        echo=True
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(TestBase.metadata.drop_all)
        await conn.run_sync(TestBase.metadata.create_all)
    
    yield engine
    await engine.dispose()

@pytest.fixture(scope="function")
async def test_session(test_engine):
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()