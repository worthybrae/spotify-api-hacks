import psycopg2
from sqlalchemy import create_engine
from database.database import Base
from dotenv import load_dotenv

load_dotenv()

# Use sync URL for setup
SYNC_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/spotify_db"

def ensure_database_exists():
    """Ensure spotify_db database exists, create if it doesn't"""
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="postgres",
            host="localhost",
            port="5432"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'spotify_db'")
        exists = cursor.fetchone()
        
        if not exists:
            print("Creating database 'spotify_db'...")
            cursor.execute('CREATE DATABASE spotify_db')
            print("Created database 'spotify_db'")
        
        cursor.close()
        conn.close()
        
        # Create tables in the database
        engine = create_engine(SYNC_DATABASE_URL)
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully")
        
    except Exception as e:
        print(f"Error in database setup: {str(e)}")
        raise