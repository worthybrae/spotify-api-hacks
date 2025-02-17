# services/redis.py
from typing import Dict
import aioredis
import json
from models.spotify import SpotifyArtist

class RedisService:
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        expiration: int = 3600  # 1 hour default expiration
    ):
        self.redis_url = redis_url
        self.expiration = expiration
        self.redis = None

    async def init(self):
        """Initialize Redis connection"""
        if self.redis is None:
            self.redis = await aioredis.from_url(
                self.redis_url, 
                decode_responses=True
            )
        return self

    async def get_artists(self, artist_ids: list[str]) -> Dict[str, SpotifyArtist]:
        """Get multiple artists by their IDs"""
        if not self.redis:
            await self.init()
            
        if not artist_ids:
            return {}
            
        artists = {}
        for artist_id in artist_ids:
            try:    
                # Check if key exists and is a string type
                key_type = await self.redis.type(artist_id)
                if key_type == "string":
                    data = await self.redis.get(artist_id)
                    if data:
                        try:
                            artists[artist_id] = SpotifyArtist(**json.loads(data))
                        except (json.JSONDecodeError, ValueError) as e:
                            print(f"Invalid JSON data for artist {artist_id}")
                            continue
            except Exception as e:
                print(f"Error retrieving artist {artist_id}: {str(e)}")
                continue
                
        return artists

    async def set_artists(self, artists: list[SpotifyArtist]) -> bool:
        """Store multiple artists with expiration"""
        if not self.redis:
            await self.init()
            
        if not artists:
            return True
            
        try:
            pipe = self.redis.pipeline()
            for artist in artists:
                # Use a prefix to distinguish artist data from Celery tasks
                pipe.set(f"artist:{artist.id}", json.dumps(artist.model_dump()), ex=self.expiration)
            
            await pipe.execute()
            return True
        except Exception as e:
            print(f"Error storing artists in Redis: {str(e)}")
            return False