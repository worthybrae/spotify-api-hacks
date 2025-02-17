// types/spotify.ts

export interface RateLimitStatus {
    window_size: number;
    current_requests: number;
    max_requests: number;
    remaining_requests: number;
    time_until_next_request: number;
    window_start: number;
    window_end: number;
  }
  
  export interface WindowRequest {
    timestamp: number;
    method: string;
    query: string;
    offset: number;
    limit: number;
    artists_found: number;
  }
  
  export interface RecentSearch {
    query: string;
    artists_found: number;
    created_at: string;
  }
  
  export interface CollectionProgress {
    timestamp: number;
    artists_added: number;
    total_artists: number;
  }
  
  export interface DashboardData {
    active_searches: string[];
    active_search_count: number;
    rate_limit_status: RateLimitStatus;
    window_requests: WindowRequest[];
    total_artists_collected: number;
    total_searches_completed: number;
    recent_searches: RecentSearch[];
    earliest_search_time: string;
  }
  
  export interface CollectionMetrics {
    hourly_progress: CollectionProgress[];
  }