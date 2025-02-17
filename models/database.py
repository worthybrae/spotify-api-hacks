from sqlalchemy import Column, Integer, String, DateTime, ARRAY
from datetime import datetime, timezone
from database.database import Base

class Artist(Base):
    __tablename__ = "artists"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    genres = Column(ARRAY(String))
    popularity = Column(Integer)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))

class SearchProgress(Base):
    __tablename__ = "search_progress"

    query = Column(String, primary_key=True)
    artists = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))