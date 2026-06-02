# API 文档

## 基础信息

- **Base URL**: `http://localhost:8000`
- **API 版本**: v1
- **认证方式**: 无需认证（本地部署）

## 响应格式

所有 API 响应均使用 JSON 格式：

```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

错误响应：

```json
{
  "code": 400,
  "message": "错误信息",
  "data": null
}
```

---

## 同步任务 API

### 启动同步任务

启动抖音收藏同步任务。

**请求**

```http
POST /api/sync/start
```

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `max_videos` | integer | 否 | 最大同步数量，默认不限制 |
| `download_cover` | boolean | 否 | 是否下载封面图，默认 `true` |

**请求示例**

```json
{
  "max_videos": 100,
  "download_cover": true
}
```

**响应**

```json
{
  "code": 200,
  "message": "同步任务已启动",
  "data": {
    "task_id": "sync_20240101_120000",
    "status": "running"
  }
}
```

**错误码**

| 错误码 | 说明 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 未登录，请先扫码登录 |
| 409 | 已有同步任务正在运行 |

---

### 查询同步状态

通过 SSE（Server-Sent Events）实时获取同步进度。

**请求**

```http
GET /api/sync/status?task_id=sync_20240101_120000
```

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `task_id` | string | 是 | 同步任务ID |

**响应（SSE 流）**

```
data: {"progress": 10, "current_title": "Python异步编程入门", "total": 100, "processed": 10}

data: {"progress": 20, "current_title": "机器学习基础", "total": 100, "processed": 20}

data: {"progress": 100, "current_title": "", "total": 100, "processed": 100, "status": "completed"}
```

**响应字段**

| 字段 | 类型 | 说明 |
|------|------|------|
| `progress` | integer | 进度百分比 (0-100) |
| `current_title` | string | 当前处理的视频标题 |
| `total` | integer | 总视频数量 |
| `processed` | integer | 已处理数量 |
| `status` | string | 任务状态：`running` / `completed` / `failed` |
| `error` | string | 错误信息（仅在失败时） |

---

### 中止同步任务

中止正在运行的同步任务。

**请求**

```http
POST /api/sync/stop
```

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `task_id` | string | 是 | 同步任务ID |

**请求示例**

```json
{
  "task_id": "sync_20240101_120000"
}
```

**响应**

```json
{
  "code": 200,
  "message": "同步任务已中止",
  "data": {
    "task_id": "sync_20240101_120000",
    "status": "stopped",
    "processed": 50
  }
}
```

---

## 视频 API

### 获取视频列表

分页获取视频列表，支持筛选。

**请求**

```http
GET /api/videos
```

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `page` | integer | 否 | 页码，默认 `1` |
| `size` | integer | 否 | 每页数量，默认 `20` |
| `category` | string | 否 | 分类筛选 |
| `tag` | string | 否 | 标签筛选 |
| `min_quality` | integer | 否 | 最低质量分 (1-10) |
| `sort_by` | string | 否 | 排序字段：`synced_at` / `quality_score` / `title` |
| `sort_order` | string | 否 | 排序顺序：`asc` / `desc` |

**请求示例**

```http
GET /api/videos?page=1&size=20&category=编程技术&sort_by=quality_score&sort_order=desc
```

**响应**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "url": "https://www.douyin.com/video/xxx",
        "title": "Python异步编程入门",
        "author": "技术博主",
        "author_id": "user_xxx",
        "desc": "详细讲解Python异步编程...",
        "cover_path": "covers/1.jpg",
        "summary": "本视频讲解了Python异步编程的核心概念...",
        "category": "编程技术",
        "tags": ["Python", "异步编程", "asyncio"],
        "key_points": ["asyncio基本用法", "await关键字", "事件循环"],
        "quality_score": 8,
        "created_at": "2024-01-01T00:00:00",
        "favorited_at": "2024-01-15T00:00:00",
        "synced_at": "2024-01-20T12:00:00"
      }
    ],
    "total": 100,
    "page": 1,
    "size": 20,
    "pages": 5
  }
}
```

---

### 获取视频详情

获取单个视频的详细信息。

**请求**

```http
GET /api/videos/:id
```

**路径参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | integer | 是 | 视频ID |

**请求示例**

```http
GET /api/videos/1
```

**响应**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "url": "https://www.douyin.com/video/xxx",
    "title": "Python异步编程入门",
    "author": "技术博主",
    "author_id": "user_xxx",
    "desc": "详细讲解Python异步编程的核心概念和实践...",
    "cover_path": "covers/1.jpg",
    "summary": "本视频详细讲解了Python异步编程的核心概念，包括asyncio事件循环、await关键字、协程的创建和使用等。适合有一定Python基础的开发者学习。",
    "category": "编程技术",
    "tags": ["Python", "异步编程", "asyncio", "协程"],
    "key_points": [
      "asyncio事件循环是异步编程的核心",
      "await关键字用于等待异步操作完成",
      "协程是轻量级的线程替代方案"
    ],
    "quality_score": 8,
    "created_at": "2024-01-01T00:00:00",
    "favorited_at": "2024-01-15T00:00:00",
    "synced_at": "2024-01-20T12:00:00",
    "similar_videos": [
      {
        "id": 5,
        "title": "Python并发编程实战",
        "similarity": 0.85
      }
    ]
  }
}
```

---

## 搜索 API

### 语义搜索

基于向量相似度的语义搜索。

**请求**

```http
POST /api/search
```

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `query` | string | 是 | 搜索查询（自然语言） |
| `limit` | integer | 否 | 返回数量，默认 `10` |
| `category` | string | 否 | 分类筛选 |
| `min_similarity` | float | 否 | 最低相似度 (0-1)，默认 `0.5` |

**请求示例**

```json
{
  "query": "如何提高专注力",
  "limit": 10,
  "category": "心理学",
  "min_similarity": 0.6
}
```

**响应**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "results": [
      {
        "id": 15,
        "title": "提高专注力的5个方法",
        "summary": "本视频介绍了5种科学提高专注力的方法...",
        "category": "心理学",
        "tags": ["专注力", "效率", "时间管理"],
        "similarity": 0.92,
        "url": "https://www.douyin.com/video/xxx"
      }
    ],
    "total": 5,
    "query": "如何提高专注力"
  }
}
```

---

## 统计 API

### 获取统计数据

获取仪表盘统计数据。

**请求**

```http
GET /api/stats
```

**响应**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "overview": {
      "total_videos": 256,
      "total_categories": 8,
      "total_tags": 45,
      "avg_quality_score": 7.2
    },
    "category_distribution": [
      {
        "category": "编程技术",
        "count": 85,
        "percentage": 33.2
      },
      {
        "category": "商业思维",
        "count": 45,
        "percentage": 17.6
      }
    ],
    "monthly_trend": [
      {
        "month": "2024-01",
        "count": 30
      },
      {
        "month": "2024-02",
        "count": 45
      }
    ],
    "top_tags": [
      {
        "tag": "Python",
        "count": 25
      },
      {
        "tag": "机器学习",
        "count": 18
      }
    ],
    "quality_distribution": [
      {
        "score": 8,
        "count": 50
      },
      {
        "score": 7,
        "count": 80
      }
    ],
    "recent_syncs": [
      {
        "id": 1,
        "title": "Python异步编程入门",
        "synced_at": "2024-01-20T12:00:00",
        "category": "编程技术"
      }
    ]
  }
}
```

---

## AI API

### 重新生成总结

对单个视频重新进行AI总结。

**请求**

```http
POST /api/ai/regenerate
```

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `video_id` | integer | 是 | 视频ID |
| `model` | string | 否 | 指定模型（覆盖默认配置） |

**请求示例**

```json
{
  "video_id": 1,
  "model": "qwen2.5:14b"
}
```

**响应**

```json
{
  "code": 200,
  "message": "总结已重新生成",
  "data": {
    "video_id": 1,
    "summary": "重新生成的总结内容...",
    "category": "编程技术",
    "tags": ["Python", "异步编程"],
    "key_points": ["要点1", "要点2"],
    "quality_score": 8
  }
}
```

---

## 登录 API

### 检查登录状态

检查抖音登录状态。

**请求**

```http
GET /api/auth/status
```

**响应**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "logged_in": true,
    "username": "用户昵称",
    "expires_at": "2024-02-20T00:00:00"
  }
}
```

### 启动登录流程

启动扫码登录流程。

**请求**

```http
POST /api/auth/login
```

**响应**

```json
{
  "code": 200,
  "message": "请扫码登录",
  "data": {
    "status": "waiting",
    "message": "浏览器已打开，请使用抖音APP扫码登录"
  }
}
```

### 退出登录

清除登录状态。

**请求**

```http
POST /api/auth/logout
```

**响应**

```json
{
  "code": 200,
  "message": "已退出登录",
  "data": {
    "logged_in": false
  }
}
```

---

## 数据管理 API

### 导出数据

导出知识库数据。

**请求**

```http
GET /api/data/export
```

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `format` | string | 否 | 导出格式：`json` / `csv` / `markdown`，默认 `json` |

**响应**

返回文件下载流。

### 清空数据

清空所有数据。

**请求**

```http
POST /api/data/clear
```

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `confirm` | boolean | 是 | 确认清空，必须为 `true` |

**请求示例**

```json
{
  "confirm": true
}
```

**响应**

```json
{
  "code": 200,
  "message": "数据已清空",
  "data": {
    "deleted_videos": 256,
    "deleted_embeddings": 256
  }
}
```

---

## 错误码汇总

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未登录 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 409 | 冲突（如已有任务运行） |
| 500 | 服务器内部错误 |

---

## 前端集成示例

### 使用 axios 调用 API

```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 30000,
});

// 启动同步
export const startSync = async (options?: { max_videos?: number }) => {
  const response = await api.post('/sync/start', options);
  return response.data;
};

// 获取视频列表
export const getVideos = async (params: {
  page?: number;
  size?: number;
  category?: string;
}) => {
  const response = await api.get('/videos', { params });
  return response.data;
};

// 语义搜索
export const searchVideos = async (query: string, limit?: number) => {
  const response = await api.post('/search', { query, limit });
  return response.data;
};

// 获取统计数据
export const getStats = async () => {
  const response = await api.get('/stats');
  return response.data;
};
```

### SSE 监听同步进度

```typescript
export const listenSyncProgress = (taskId: string, onProgress: (data: any) => void) => {
  const eventSource = new EventSource(`http://localhost:8000/api/sync/status?task_id=${taskId}`);
  
  eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    onProgress(data);
    
    if (data.status === 'completed' || data.status === 'failed') {
      eventSource.close();
    }
  };
  
  eventSource.onerror = () => {
    eventSource.close();
  };
  
  return () => eventSource.close();
};
```
