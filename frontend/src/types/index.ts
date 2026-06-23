/**
 * 视频类型
 */
export interface Video {
  id: number;
  url: string;
  title: string;
  author: string;
  author_id: string;
  desc: string;
  cover_path: string;
  cover_url: string;
  summary: string;
  category: string;
  tags: string[];
  key_points: string[];
  quality_score: number;
  created_at: string | null;
  favorited_at: string | null;
  synced_at: string | null;
  updated_at: string | null;
  embedding_id: string | null;
  similarity?: number;
}

/**
 * 视频列表响应
 */
export interface VideoListResponse {
  items: Video[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

/**
 * 同步任务
 */
export interface SyncTask {
  task_id: string;
  status: 'running' | 'completed' | 'failed' | 'stopped';
  progress: number;
  total: number;
  processed: number;
  current_title: string;
  error: string | null;
}

/**
 * 分类分布
 */
export interface CategoryDistribution {
  category: string;
  count: number;
  percentage: number;
}

/**
 * 最近同步
 */
export interface RecentSync {
  id: number;
  title: string;
  category: string;
  quality_score: number;
  synced_at: string | null;
}

/**
 * 作者统计
 */
export interface AuthorStat {
  author: string;
  count: number;
}

/**
 * 月度统计
 */
export interface MonthlyStat {
  month: string;
  count: number;
}

/**
 * 统计信息
 */
export interface Stats {
  overview: {
    total_videos: number;
    total_categories: number;
    total_embeddings?: number;
    avg_quality_score: number;
  };
  category_distribution: Record<string, number>;
  top_authors: AuthorStat[];
  monthly_stats: MonthlyStat[];
  recent_syncs: RecentSync[];
}

/**
 * 搜索结果
 */
export interface SearchResult {
  results: Video[];
  total: number;
  query: string;
  mode: string;
}

/**
 * 认证状态
 */
export interface AuthStatus {
  logged_in: boolean;
  is_expired?: boolean;
  message: string;
  details?: {
    exists: boolean;
    valid: boolean;
    message: string;
    cookies_count?: number;
    last_modified?: string;
    age_days?: number;
  };
}

/**
 * 健康检查响应
 */
export interface HealthStatus {
  status: 'ok' | 'error';
  database: 'ok' | 'error';
  chromadb: 'ok' | 'error';
  auth: 'ok' | 'not_configured';
}

/**
 * 配置状态
 */
export interface ConfigStatus {
  ai_provider: string;
  has_api_key: boolean;
  api_key_preview: string | null;
  auth_status: {
    exists: boolean;
    valid: boolean;
  };
}

/**
 * 分类
 */
export interface Category {
  name: string;
  count: number;
}

/**
 * 标签
 */
export interface Tag {
  name: string;
  count: number;
}
