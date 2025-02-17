# Spotify Artist Collection System

A distributed system for efficiently collecting all artist data from the Spotify API while respecting rate limits. The system uses a combination of FastAPI, Celery, Redis, and PostgreSQL to create a resilient and scalable artist data collection pipeline.

## Project Overview

This project implements a systematic approach to collect artist data from Spotify's API, working around the limitation that there's no direct endpoint to get all artists. Instead, it:

1. Generates systematic search strings (0000-zzzz) to exhaustively search the Spotify catalog
2. Uses a distributed task queue (Celery) to parallelize API requests
3. Implements intelligent rate limiting and backoff strategies
4. Provides a real-time monitoring dashboard to track progress
5. Stores data reliably in PostgreSQL with Redis caching

### Key Features

- **Systematic Search**: Generates all possible 4-character combinations to search the Spotify API
- **Rate Limit Management**: Sophisticated rate limiting using Redis to track API requests
- **Distributed Processing**: Uses Celery for task distribution and parallel processing
- **Real-time Monitoring**: React dashboard showing progress, rate limits, and statistics
- **Resilient Design**: Handles API errors, rate limits, and process failures gracefully
- **Data Integrity**: Ensures no duplicate searches or data loss

## Project Structure

```
├── api.py                 # FastAPI routes and endpoints
├── celery_config.py       # Celery configuration
├── tasks.py              # Celery task definitions
├── database/
│   ├── database.py       # Database connection and session management
│   └── setup.py          # Database initialization
├── models/
│   ├── database.py       # SQLAlchemy models
│   └── spotify.py        # Pydantic models for Spotify data
├── config/
│   └── rate_limits.py    # Setting hard coded rate limit thresholds
├── services/
│   ├── spotify.py        # Spotify API client
│   ├── redis.py          # Redis service for rate limiting
│   ├── database.py       # Database operations service
│   └── search_generator.py # Search string generation logic
├── frontend/
│   ├── components/
│   │   ├── SpotifyDashboard.tsx    # Main dashboard component
│   │   ├── MetricCard.tsx          # Metric display component
│   │   ├── RequestsTable.tsx       # API requests table
│   │   └── SearchesTable.tsx       # Completed searches table
│   └── types/
│       └── spotify.ts              # TypeScript interfaces
└── requirements.txt                # Python dependencies
```

## Technical Design

### Backend Components

1. **Search String Generator**

   - Systematically generates 4-character search strings (0000-zzzz)
   - Tracks progress through the search space
   - Ensures no duplicate searches

2. **Rate Limiter**

   - Uses Redis to track API request windows
   - Implements sliding window rate limiting
   - Handles backoff and retry logic

3. **Task Queue**

   - Celery tasks for search string generation and API requests
   - Parallel processing with configurable worker count
   - Automatic task retries with exponential backoff

4. **Data Storage**
   - PostgreSQL for permanent storage
   - Redis for rate limit tracking and temporary data
   - Atomic operations for data consistency

### Monitoring Dashboards

#### React Frontend Dashboard

- Real-time metrics and progress tracking
- API request visualization
- Search completion statistics
- Rate limit monitoring

#### Flower Dashboard

- Real-time Celery task monitoring
- Worker status and statistics
- Task success/failure rates
- Queue lengths and processing times
- Resource usage metrics

## Local Setup Guide

### Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Redis

### Backend Setup

1. Create a Python virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:

```bash
# Create .env file with:
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
```

4. Start the backend services:

```bash
# Terminal 1 - FastAPI
uvicorn api:app --reload

# Terminal 2 - Celery Worker
celery -A celery_config worker --loglevel=INFO

# Terminal 3 - Celery Beat
celery -A celery_config beat --loglevel=INFO

# Terminal 4 - Flower Dashboard
celery -A celery_config flower --port=5555
```

### Frontend Setup

1. Install dependencies:

```bash
cd frontend
npm install
```

2. Start the development server:

```bash
npm run dev
```

The React dashboard will be available at `http://localhost:5173`
The Flower dashboard will be available at `http://localhost:5555`

## Usage

Once all services are running:

1. The system will automatically start generating search strings and queuing searches
2. Monitor progress through the dashboard
3. The collection process will continue until all possible search strings are exhausted

## Rate Limiting Details

The system implements a sophisticated rate limiting strategy:

- 10 requests per 30-second window per IP
- Automatic backoff on rate limit errors
- Redis-based sliding window implementation
- Distributed rate limit tracking across workers

## Error Handling

The system handles various error scenarios:

- API rate limiting
- Network failures
- Database connection issues
- Process crashes
- Duplicate searches
- Invalid responses

Each error type has specific retry and recovery logic to ensure data collection continues reliably.

## Testing

- The test suite is very limited right now and should be expanded upon to have proper coverage. With more time, I would add a lot more coverage of the functionality of this system

To run the tests use:

```
pytest --cov=services --cov=api tests/ -v
```
