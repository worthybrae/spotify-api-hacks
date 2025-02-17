from typing import List
from sqlalchemy import select, desc
from models.database import SearchProgress
from database.database import AsyncSessionLocal
import os
from dotenv import load_dotenv
import multiprocessing


load_dotenv()

class SearchStringGenerator:
    """Maintains search string state with batch generation starting with letters"""
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SearchStringGenerator, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.current = None
            self._initialized = True
            self.max_workers = min(
                int(os.getenv('MAX_WORKERS', multiprocessing.cpu_count() * 2)),
                10  # Cap at 10 due to Spotify API rate limits
            )
            # Define valid characters with letters first, then numbers
            self.valid_chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
    
    @staticmethod
    def char_increment(s: str) -> str:
        """
        Increment string with support for letters and numbers.
        Goes from a-z, then 0-9.
        """
        if not s:
            return 'a'  # Start with 'a' if empty
            
        # Convert last character to next in sequence
        valid_chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
        last_char = s[-1]
        
        if last_char not in valid_chars:
            return s[:-1] + 'a'
            
        current_index = valid_chars.index(last_char)
        if current_index < len(valid_chars) - 1:
            return s[:-1] + valid_chars[current_index + 1]
            
        # If we've reached '9', increment the next position
        return SearchStringGenerator.char_increment(s[:-1]) + 'a'
    
    async def initialize(self) -> None:
        """Initialize search string state from database"""
        if self.current is None:
            async with AsyncSessionLocal() as session:
                query = select(SearchProgress.query).order_by(desc(SearchProgress.query)).limit(1)
                result = await session.execute(query)
                last_search = result.scalar()
                
                # If no previous searches, start with 'aaaa'
                # If there are previous searches, start with next string
                if not last_search:
                    self.current = 'aaaa'
                else:
                    self.current = last_search  # Next string will be generated in generate_batch

    async def generate_batch(self) -> List[str]:
        """Generate a full batch of search strings based on available capacity"""
        await self.initialize()
        strings = []
        current = self.current
        
        # For new searches (starting from 'aaaa'), include the first string
        # For continuing searches, skip the first increment
        if current == 'aaaa' and not strings:
            strings.append(current)
            current = self.char_increment(current)
        
        # Generate remaining strings up to max_workers
        remaining = self.max_workers - len(strings)
        for _ in range(remaining):
            current = self.char_increment(current)
            strings.append(current)
            
        self.current = current
        return strings