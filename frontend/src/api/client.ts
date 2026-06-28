/**
 * API 客户端封装
 * 使用 Vite proxy，无需硬编码后端地址
 */

const API_BASE = '';  // 使用 Vite proxy，相对路径即可

interface RequestOptions {
  method?: string;
  body?: unknown;
  headers?: Record<string, string>;
}

async function request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, headers = {} } = options;

  const response = await fetch(`${API_BASE}${endpoint}`, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '请求失败' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

// 健康检查
export async function checkHealth() {
  return request<{ status: string; auth_exists: boolean }>('/health');
}

// 获取视频列表
export async function getVideos(limit = 100, offset = 0, category?: string) {
  const params = new URLSearchParams({ limit: String(limit), offset: String(offset) });
  if (category) params.append('category', category);
  return request<{ items: unknown[]; total: number }>(`/api/videos?${params}`);
}

// 获取分类列表
export async function getCategories() {
  return request<{ categories: string[] }>('/api/videos/categories');
}

// 启动同步
export async function startSync(limit = 10) {
  return request<{ task_id: string; status: string; message: string }>(
    `/api/sync/start?limit=${limit}`,
    { method: 'POST' }
  );
}

// 停止同步
export async function stopSync(taskId?: string) {
  const params = taskId ? `?task_id=${taskId}` : '';
  return request<{ message: string; task_id: string }>(
    `/api/sync/stop${params}`,
    { method: 'POST' }
  );
}

// 创建 SSE 连接（修复 #7: 增加 onError 回调）
export function createSyncSSE(
  taskId: string,
  onMessage: (data: unknown) => void,
  onError?: () => void
) {
  const eventSource = new EventSource(`/api/sync/status/${taskId}`);

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch {
      // 忽略解析错误
    }
  };

  eventSource.onerror = () => {
    eventSource.close();
    onError?.();  // 通知调用方连接断开
  };

  return eventSource;
}

// 退出登录
export async function logout() {
  return request<{ success: boolean; logged_in: boolean; message: string }>(
    '/api/auth/logout',
    { method: 'POST' }
  );
}
