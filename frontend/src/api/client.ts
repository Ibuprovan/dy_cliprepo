import axios from 'axios';
import type {
  VideoListResponse,
  Video,
  Stats,
  SearchResult,
  AuthStatus,
} from '../types';

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
});

export async function checkAuth(): Promise<AuthStatus> {
  const res = await api.get('/auth/status');
  return res.data;
}

export async function login(): Promise<{ status: string; message: string }> {
  const res = await api.post('/auth/login');
  return res.data;
}

export async function confirmLogin(): Promise<{ status: string; message: string }> {
  const res = await api.post('/auth/confirm');
  return res.data;
}

export async function logout(): Promise<{ status: string; message: string }> {
  const res = await api.post('/auth/logout');
  return res.data;
}

export async function startSync(maxVideos?: number): Promise<{ task_id: string; status: string }> {
  const params = maxVideos ? { max_videos: maxVideos } : {};
  const res = await api.post('/sync/start', null, { params });
  return res.data;
}

export async function stopSync(taskId: string): Promise<{ message: string }> {
  const res = await api.post('/sync/stop', null, { params: { task_id: taskId } });
  return res.data;
}

export async function getVideos(params: {
  page?: number;
  size?: number;
  category?: string;
  tag?: string;
  min_quality?: number;
  sort_by?: string;
  sort_order?: string;
} = {}): Promise<VideoListResponse> {
  const res = await api.get('/videos', { params });
  return res.data;
}

export async function getVideoById(id: number): Promise<Video> {
  const res = await api.get(`/videos/${id}`);
  return res.data;
}

export async function searchVideos(query: string, limit = 10, mode = 'semantic'): Promise<SearchResult> {
  const res = await api.post('/search', { query, limit, mode });
  return res.data;
}

export async function getStats(): Promise<Stats> {
  const res = await api.get('/stats');
  return res.data;
}

export function createSyncEventSource(taskId: string): EventSource {
  return new EventSource(`/api/sync/status?task_id=${taskId}`);
}
