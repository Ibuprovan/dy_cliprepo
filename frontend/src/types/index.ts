export interface Video {
  id: number;
  url: string;
  title: string;
  author: string;
  author_id: string;
  desc: string;
  cover_path: string;
  summary: string;
  category: string;
  tags: string[];
  key_points: string[];
  quality_score: number;
  created_at: string | null;
  favorited_at: string | null;
  synced_at: string | null;
  embedding_id: string | null;
  similarity?: number;
}

export interface VideoListResponse {
  items: Video[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface SyncTask {
  task_id: string;
  status: string;
  progress: number;
  total: number;
  processed: number;
  current_title: string;
  error: string | null;
}

export interface CategoryDistribution {
  category: string;
  count: number;
  percentage: number;
}

export interface RecentSync {
  id: number;
  title: string;
  category: string;
  synced_at: string | null;
}

export interface Stats {
  overview: {
    total_videos: number;
    total_categories: number;
    total_embeddings?: number;
    avg_quality_score: number;
  };
  category_distribution: CategoryDistribution[];
  recent_syncs: RecentSync[];
}

export interface SearchResult {
  results: Video[];
  total: number;
  query: string;
  mode: string;
}

export interface AuthStatus {
  logged_in: boolean;
  message: string;
}
