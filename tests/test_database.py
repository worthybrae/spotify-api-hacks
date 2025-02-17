# tests/test_database.py
import pytest
from unittest.mock import patch
from sqlalchemy.ext.asyncio import AsyncSession
from services.database import DatabaseService
from models.spotify import SpotifyArtist
from tests.conftest import TestArtist

@pytest.mark.asyncio
@patch('services.database.Artist', TestArtist)  # Mock the real Artist with TestArtist
async def test_upsert_artists(test_session: AsyncSession):
    """Test upserting artists"""
    db_service = DatabaseService(test_session)
    test_artist = SpotifyArtist(
        id="test_id",
        name="Test Artist",
        genres=["rock"],
        popularity=80
    )
    
    # Test inserting
    result = await db_service.upsert_artists([test_artist])
    assert len(result) == 1
    assert "test_id" in result

    # Test upserting the same artist
    updated_artist = SpotifyArtist(
        id="test_id",
        name="Updated Artist",
        genres=["rock", "pop"],
        popularity=85
    )
    result = await db_service.upsert_artists([updated_artist])
    assert len(result) == 1