from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class SpotifyToken(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    expires_at: datetime = Field(default_factory=lambda: datetime.now())

class SpotifyAuthError(BaseModel):
    error: str
    error_description: str

class SpotifyArtist(BaseModel):
    id: str
    name: str
    genres: List[str]
    popularity: int

class SpotifyArtists(BaseModel):
    artists: List[SpotifyArtist]

