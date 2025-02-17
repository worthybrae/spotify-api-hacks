# tests/test_api.py
from fastapi.testclient import TestClient
from unittest.mock import patch
from api import app
from tests.conftest import TestArtist

# Mock the database models before importing app
with patch('models.database.Artist', TestArtist):
    client = TestClient(app)

@patch('services.spotify.SpotifyClient.search_artists')
@patch('services.redis.RedisService.get_rate_limit_info')
def test_search_endpoint(mock_rate_limit, mock_search):
    # Setup mock returns
    mock_search.return_value = {
        "artists": [
            {
                "id": "test_id",
                "name": "Test Artist",
                "genres": ["rock"],
                "popularity": 80
            }
        ]
    }
    mock_rate_limit.return_value = {
        "remaining_requests": 10,
        "time_until_next_request": 0
    }

    response = client.get("/search?q=test")
    assert response.status_code == 200
    data = response.json()
    assert "artists" in data