from typing import Dict

# Spotify API rate limits
SPOTIFY_RATE_LIMIT = {
    "window_seconds": 30,
    "max_requests": 10
}

# Convert to Celery rate limit format (requests/minute)
CELERY_RATE_LIMIT = f"{int(SPOTIFY_RATE_LIMIT['max_requests'] * (60 / SPOTIFY_RATE_LIMIT['window_seconds']))}/m"

# Redis configuration
REDIS_CONFIG = {
    "rate_limit_window": SPOTIFY_RATE_LIMIT["window_seconds"],
    "rate_limit_max": SPOTIFY_RATE_LIMIT["max_requests"]
}

def get_spotify_rate_limit() -> Dict[str, int]:
    return SPOTIFY_RATE_LIMIT

def get_celery_rate_limit() -> str:
    return CELERY_RATE_LIMIT

def get_redis_rate_limit() -> Dict[str, int]:
    return REDIS_CONFIG