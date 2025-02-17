# services/spotify.py
from typing import Optional, Dict, List
from datetime import timedelta, datetime
import httpx
from models.spotify import SpotifyToken
from research.redis import RedisService
from services.database import DatabaseService

class SpotifyClient:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        base_url: str = "https://api.spotify.com/v1",
        auth_url: str = "https://accounts.spotify.com/api/token"
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url
        self.auth_url = auth_url
        self._current_token: Optional[SpotifyToken] = None

    # AUTH FUNCTIONS
    def _is_token_valid(self) -> bool:
        """Check if current token exists and is still valid"""
        if not self._current_token:
            return False
        # Add 5 minute buffer before expiration
        expiration_buffer = timedelta(minutes=5)
        return datetime.now() < self._current_token.expires_at - expiration_buffer

    async def _get_access_token(self) -> SpotifyToken:
        """Get a valid access token, either from cache or by requesting a new one"""
        if self._is_token_valid():
            return self._current_token

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.auth_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
            
            token_data = response.json()
            token_data["expires_at"] = datetime.now() + timedelta(seconds=token_data["expires_in"])
            
            self._current_token = SpotifyToken(**token_data)
            return self._current_token

    async def _get_headers(self) -> Dict[str, str]:
        """Get headers with valid access token"""
        token = await self._get_access_token()
        return {
            "Authorization": f"Bearer {token.access_token}",
            "Content-Type": "application/json"
        }

    # EXTRACTION FUNCTIONS
    # Get Up To 50 Artist Profiles
    async def get_artists(
        self, 
        artist_ids: List[str],
        redis_service: Optional[RedisService] = None,
        db_service: Optional[DatabaseService] = None
    ) -> ArtistsResponse:
        """
        Get Spotify catalog information for several artists based on their IDs.
        Uses optimistic Redis removal to prevent concurrent processing of same IDs.
        
        Args:
            artist_ids: List of Spotify artist IDs. Maximum: 50 IDs.
            redis_service: Optional RedisService for cleaning up processed IDs
            db_service: Optional DatabaseService for persisting artist data
                
        Returns:
            ArtistsResponse containing list of Artist objects
                
        Raises:
            ValueError: If more than 50 artist IDs are provided
            httpx.HTTPError: If the API request fails
        """
        if len(artist_ids) > 50:
            raise ValueError("Maximum of 50 artist IDs allowed per request")
        
        # Optimistically remove IDs from Redis if service provided
        if redis_service:
            await redis_service.remove_artist_ids(set(artist_ids))
                
        try:
            async with httpx.AsyncClient() as client:
                headers = await self._get_headers()
                response = await client.get(
                    f"{self.base_url}/artists",
                    headers=headers,
                    params={"ids": ",".join(artist_ids)}
                )
                response.raise_for_status()
                artists_response = ArtistsResponse(**response.json())
                
                # If database service provided, persist the data
                if db_service:
                    try:
                        await db_service.upsert_artists(artists_response.artists)
                    except Exception as e:
                        # Log database error but don't fail request
                        print(f"Error persisting artists to database: {str(e)}")
                        # Add IDs back to Redis on database failure
                        if redis_service:
                            await redis_service.add_artist_ids(set(artist_ids))
                        
                return artists_response
                
        except Exception as e:
            # On any error, add IDs back to Redis if service provided
            if redis_service:
                await redis_service.add_artist_ids(set(artist_ids))
            raise e
    # Get Up To 20 Albums    
    async def get_albums(self, album_ids: List[str]) -> AlbumsResponse:
        """
        Get Spotify catalog information for several albums based on their IDs.
        
        Args:
            album_ids: List of Spotify album IDs. Maximum: 20 IDs.
            
        Returns:
            AlbumsResponse containing list of Album objects
            
        Raises:
            ValueError: If more than 20 album IDs are provided
            httpx.HTTPError: If the API request fails
        """
        if len(album_ids) > 20:
            raise ValueError("Maximum of 20 album IDs allowed per request")
            
        async with httpx.AsyncClient() as client:
            headers = await self._get_headers()
            response = await client.get(
                f"{self.base_url}/albums",
                headers=headers,
                params={"ids": ",".join(album_ids)}
            )
            response.raise_for_status()
            return AlbumsResponse(**response.json())
    # Get All Featured Artist ID's from a List of Album ID's
    async def get_album_artists(
        self, 
        album_ids: List[str],
        redis_service: Optional[RedisService] = None,
        db_service: Optional[DatabaseService] = None
    ) -> AlbumArtistsResponse:
        """
        Get all unique artist IDs that appear in the albums' tracks.
        Uses optimistic Redis removal to prevent concurrent processing of same IDs.
        
        Args:
            album_ids: List of Spotify album IDs. Maximum: 20 IDs.
            redis_service: Optional RedisService for Redis operations
            db_service: Optional DatabaseService for database operations
        
        Returns:
            AlbumArtistsResponse containing list of unique artist IDs
        """
        # Optimistically remove album IDs from Redis if service provided
        if redis_service:
            await redis_service.remove_album_ids(set(album_ids))
        
        try:
            albums_response = await self.get_albums(album_ids)
            
            # Use a set for efficient duplicate removal
            artist_ids = set()
            
            for album in albums_response.albums:
                # Add artists from each track
                for track in album.tracks.items:
                    for artist in track.artists:
                        artist_ids.add(artist.id)
            
            # If database service provided, handle database operations
            if db_service:
                try:
                    # Insert albums into database
                    await db_service.upsert_albums(album_ids)
                    
                    # Find which artists don't exist in database
                    missing_artist_ids = await db_service.get_missing_artist_ids(list(artist_ids))
                    
                    # Add missing artists to Redis queue
                    if missing_artist_ids and redis_service:
                        await redis_service.add_artist_ids(missing_artist_ids)
                        
                except Exception as e:
                    # Log database error but don't fail request
                    print(f"Error handling database operations: {str(e)}")
                    # Add album IDs back to Redis on database failure
                    if redis_service:
                        await redis_service.add_album_ids(set(album_ids))
            
            return AlbumArtistsResponse(
                artist_ids=list(artist_ids)
            )
            
        except Exception as e:
            # On any error, add album IDs back to Redis if service provided
            if redis_service:
                await redis_service.add_album_ids(set(album_ids))
            raise e
    
    # SEARCH FUNCTIONS
    # Search for 50 Albums Given a Query String
    async def search_albums(
        self,
        query: str,
        limit: int = 50,
        offset: int = 0,
        redis_service: Optional[RedisService] = None,
        db_service: Optional[DatabaseService] = None
    ) -> SearchIdsResponse:
        """
        Search for albums and return unique album and artist IDs.
        If services are provided, adds new IDs to Redis sets after checking DB.
        
        Args:
            query: Search query string
            limit: Maximum number of results (default: 50, max: 50)
            offset: The index of the first result (default: 0)
            redis_service: Optional RedisService instance for caching IDs
            db_service: Optional DatabaseService instance for checking existing records
                
        Returns:
            SearchIdsResponse containing lists of unique album and artist IDs
        """
        if limit > 50:
            raise ValueError("Maximum limit is 50")
                
        async with httpx.AsyncClient() as client:
            headers = await self._get_headers()
            response = await client.get(
                f"{self.base_url}/search",
                headers=headers,
                params={
                    "q": query,
                    "type": "album",
                    "limit": limit,
                    "offset": offset
                }
            )
            response.raise_for_status()
                
            search_results = response.json()
                
            # Extract unique IDs using sets
            album_ids = set()
            artist_ids = set()
                
            for album in search_results["albums"]["items"]:
                album_ids.add(album["id"])
                for artist in album["artists"]:
                    artist_ids.add(artist["id"])

            # If services provided, check DB and add missing IDs to Redis
            if redis_service and db_service:
                # Get IDs that don't exist in DB
                missing_album_ids = await db_service.get_missing_album_ids(list(album_ids))
                missing_artist_ids = await db_service.get_missing_artist_ids(list(artist_ids))
                
                # Add missing IDs to Redis
                if missing_album_ids:
                    await redis_service.add_album_ids(list(missing_album_ids))
                if missing_artist_ids:
                    await redis_service.add_artist_ids(list(missing_artist_ids))
                            
            return SearchIdsResponse(
                album_ids=list(album_ids),
                artist_ids=list(artist_ids)
            )
        