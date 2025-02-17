


    # Probably Misc
    # Get Top 10 Songs For Given Artist
    async def get_artist_top_tracks(self, artist_id: str) -> TopTracksResponse:
        """Get an artist's top tracks"""
        async with httpx.AsyncClient() as client:
            headers = await self._get_headers()
            response = await client.get(
                f"{self.base_url}/artists/{artist_id}/top-tracks",
                headers=headers
            )
            response.raise_for_status()
            return TopTracksResponse(**response.json())
    # Extract Featured Artist ID's from Top Songs
    async def get_artist_collaborators(self, artist_id: str) -> CollaboratorResponse:
        """
        Get unique artist IDs that appear in the artist's top tracks (excluding the original artist)
        """
        top_tracks = await self.get_artist_top_tracks(artist_id)
        
        # Collect all artist IDs from tracks
        collaborator_ids = set()
        for track in top_tracks.tracks:
            
            for artist in track["artists"]:
                # Exclude the original artist
                if artist["id"] != artist_id:
                    collaborator_ids.add(artist["id"])
        
        return CollaboratorResponse(artist_ids=list(collaborator_ids))
    # Get 50 New Releases from Spotify
    async def get_new_releases(
        self, 
        limit: int = 50,
        offset: int = 0
    ) -> NewReleasesIdsResponse:
        """
        Get a list of new album releases and extract all unique album and artist IDs
        
        Args:
            limit: Maximum number of items to return (default: 20, max: 50)
            offset: Offset for pagination (default: 0)
            
        Returns:
            NewReleasesIdsResponse containing lists of unique album and artist IDs
        """
        if limit > 50:
            raise ValueError("Maximum limit is 50")
            
        async with httpx.AsyncClient() as client:
            headers = await self._get_headers()
            response = await client.get(
                f"{self.base_url}/browse/new-releases",
                headers=headers,
                params={
                    "limit": limit,
                    "offset": offset
                }
            )
            response.raise_for_status()
            
            new_releases = NewReleasesResponse(**response.json())
            
            # Extract unique IDs using sets
            album_ids = set()
            artist_ids = set()
            
            for album in new_releases.albums.items:
                album_ids.add(album.id)
                for artist in album.artists:
                    artist_ids.add(artist.id)
                    
            return NewReleasesIdsResponse(
                album_ids=list(album_ids),
                artist_ids=list(artist_ids)
            )

@app.get("/artists/{artist_id}/collaborators", response_model=CollaboratorResponse)
async def get_artist_top_song_collaborators(
    artist_id: str,
    spotify_client: SpotifyClient = Depends(get_spotify_client)
):
    """Get all unique artist IDs that appear in an artist's top tracks"""
    try:
        return await spotify_client.get_artist_collaborators(artist_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except httpx.HTTPError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    
@app.get("/new-releases", response_model=NewReleasesIdsResponse)
async def get_new_releases(
    limit: int = Query(default=50, le=50, gt=0),
    offset: int = Query(default=0, ge=0, le=50),
    spotify_client: SpotifyClient = Depends(get_spotify_client)
):
    """
    Get all unique album and artist IDs from Spotify's new releases.
    Run this twice per day to get top 100 new album releases (can only be run twice)
    
    Args:
        limit: Maximum number of items (1-50, default 50)
        offset: Offset for pagination (default 0, max 100)
    """
    try:
        return await spotify_client.get_new_releases(limit=limit, offset=offset)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except httpx.HTTPError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    
@app.get("/artists", response_model=ArtistsResponse)
async def get_artists(
    ids: str,
    spotify_client: SpotifyClient = Depends(get_spotify_client),
    redis_service: RedisService = Depends(get_redis_service),
    db: AsyncSession = Depends(get_db)
):
    try:
        artist_ids = ids.split(",")
        db_service = DatabaseService(db)
        return await spotify_client.get_artists(
            artist_ids=artist_ids,
            redis_service=redis_service,
            db_service=db_service
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except httpx.HTTPError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    
@app.get("/albums/featured-artists", response_model=AlbumArtistsResponse)
async def get_album_featured_artists(
    ids: str,
    spotify_client: SpotifyClient = Depends(get_spotify_client),
    redis_service: RedisService = Depends(get_redis_service),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all unique artist IDs that appear in the albums' tracks
    """
    try:
        album_ids = ids.split(",")
        db_service = DatabaseService(db)
        return await spotify_client.get_album_artists(
            album_ids=album_ids,
            redis_service=redis_service,
            db_service=db_service
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except httpx.HTTPError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))