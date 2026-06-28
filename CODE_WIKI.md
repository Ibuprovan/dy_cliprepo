# 抖音收藏 AI 知识库 - Code Wiki

> 抖音收藏视频的智能总结与展示系统，基于 Playwright 抓取 + GLM 多模态 AI 总结 + 语义搜索（规划中）。

---

## 目录

1. [项目概述](#1-项目概述)
2. [整体架构](#2-整体架构)
3. [后端架构详解](#3-后端架构详解)
4. [前端架构详解](#4-前端架构详解)
5. [核心数据模型](#5-核心数据模型)
6. [API 接口文档](#6-api-接口文档)
7. [关键流程说明](#7-关键流程说明)
8. [配置与环境](#8-配置与环境)
9. [开发与运行](#9-开发与运行)
10. [已知问题与注意事项](#10-已知问题与注意事项)

---

## 1. 项目概述

### 1.1 项目定位

本地工具，通过 Playwright 无头浏览器抓取抖音收藏视频，使用 GLM-4.6V-Flash 多模态模型进行 AI 总结和分类，提供 Web 界面进行浏览、筛选和管理。

### 1.2 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| 后端框架 | FastAPI | 0.115.0 |
| 异步服务 | Uvicorn | 0.30.0 |
| 浏览器自动化 | Playwright | 1.48.0 |
| 数据验证 | Pydantic | 2.9.0 |
| 数据库 | SQLite (aiosqlite) | 0.20.0 |
| HTTP 客户端 | httpx | 0.27.0 |
| AI 模型 | 智谱 GLM-4.6V-Flash | - |
| 前端框架 | React + TypeScript | React 19.2.6 |
| 构建工具 | Vite | 8.0.12 |
| UI 样式 | Tailwind CSS v4 | 4.3.0 |

### 1.3 项目特性

- ✅ 抖音收藏视频无头抓取
- ✅ 视频详情页完整描述提取
- ✅ GLM-4.6V-Flash 双路由 AI 总结（TEXT / VL 模式）
- ✅ AI 自动分类（12 个预设分类）
- ✅ 视频卡片展示 + 分类筛选
- ✅ 批量删除 + 全选
- ✅ Markdown 导出
- ✅ 实时同步进度（SSE）
- ✅ 环形缓冲区调试日志系统
- ⏳ 语义搜索（规划中）
- ⏳ 本地 VL 模型（规划中）

---

## 2. 整体架构

### 2.1 架构图

```
┌─────────────────────────────────────────────────────────┐
│                        前端 (React)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │
│  │  Layout  │  │ SyncPanel│  │     VideoTable       │  │
│  └──────────┘  └──────────┘  └──────────────────────┘  │
│                       │                                 │
│                  API Client (fetch)                     │
└───────────────────────┼─────────────────────────────────┘
                        │ HTTP :5173 (dev) / 同端口 (prod)
                        ▼
┌─────────────────────────────────────────────────────────┐
│                   后端 (FastAPI :8000)                   │
│  ┌───────────────────────────────────────────────────┐  │
│  │                    API Layer                      │  │
│  │  health / videos / sync / auth / debug            │  │
│  └───────────────────────┬───────────────────────────┘  │
│                          │                              │
│  ┌───────────────────────▼───────────────────────────┐  │
│  │                  Service Layer                    │  │
│  │  sync_service (独立线程)  │  ai_service           │  │
│  └───────────────┬───────────────┬───────────────────┘  │
│                  │               │                      │
│  ┌───────────────▼───────────────▼───────────────────┐  │
│  │               Repository Layer                    │  │
│  │       video_repo        │      task_repo          │  │
│  └───────────────┬───────────────┬───────────────────┘  │
│                  │               │                      │
│  ┌───────────────▼───────────────▼───────────────────┐  │
│  │                Database (SQLite)                  │  │
│  │  videos 表  │  sync_tasks 表  │  WAL 模式          │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │               Scraper Layer (Playwright)          │  │
│  │  auth_manager  │  sync_engine  │  selectors       │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
              ┌──────────────────┐
              │   抖音 Web 平台   │
              └──────────────────┘
```

### 2.2 分层架构说明

| 层级 | 职责 | 关键模块 |
|------|------|----------|
| API 层 | 路由定义、请求验证、响应序列化 | `app/api/v1/` |
| Service 层 | 业务逻辑编排、事务协调 | `app/services/` |
| Repository 层 | 数据访问封装、SQL 注入防护 | `app/repositories/` |
| Scraper 层 | Playwright 浏览器自动化、页面解析 | `app/scraper/` |
| Core 层 | 配置管理、日志系统 | `app/core/` |
| DB 层 | 数据库连接、表初始化 | `app/db/` |
| Models 层 | Pydantic 数据模型定义 | `app/models/` |

### 2.3 目录结构

```
dy_cliprepo/
├── backend/                          # 后端代码
│   ├── app/
│   │   ├── main.py                   # FastAPI 入口，lifespan 管理
│   │   ├── api/v1/                   # API 路由层
│   │   │   ├── health.py             # 健康检查
│   │   │   ├── videos.py             # 视频 CRUD
│   │   │   ├── sync.py               # 同步任务（SSE）
│   │   │   ├── auth.py               # 登录状态管理
│   │   │   └── debug.py              # 调试日志
│   │   ├── core/                     # 核心配置
│   │   │   ├── config.py             # 全局配置 + 路径管理
│   │   │   └── logger.py             # 环形缓冲区日志系统
│   │   ├── db/                       # 数据库层
│   │   │   └── database.py           # aiosqlite 单例 + 表初始化
│   │   ├── models/                   # 数据模型
│   │   │   └── video.py              # VideoCreate/VideoDB/VideoResponse
│   │   ├── repositories/             # 数据仓库层
│   │   │   ├── video_repo.py         # 视频 CRUD
│   │   │   └── task_repo.py          # 同步任务状态
│   │   ├── scraper/                  # 爬虫层
│   │   │   ├── auth_manager.py       # 登录态管理
│   │   │   ├── sync_engine.py        # 同步引擎（Playwright）
│   │   │   └── selectors.py          # CSS 选择器集中管理
│   │   └── services/                 # 业务服务层
│   │       ├── sync_service.py       # 同步任务服务（独立线程）
│   │       └── ai_service.py         # AI 总结 + 分类
│   ├── run_server.py                 # 后端启动脚本（Windows 兼容）
│   ├── login_manual.py               # 手动登录脚本
│   ├── test_sync.py                  # 同步测试脚本
│   ├── diagnose.py                   # 环境诊断
│   ├── requirements.txt              # Python 依赖
│   └── .env.example                  # 环境变量示例
├── frontend/                         # 前端代码
│   ├── src/
│   │   ├── App.tsx                   # 主应用组件
│   │   ├── main.tsx                  # 入口文件
│   │   ├── api/client.ts             # API 客户端封装
│   │   ├── hooks/useSync.ts          # 同步状态 Hook (SSE)
│   │   ├── components/               # UI 组件
│   │   │   ├── Layout.tsx            # 布局组件
│   │   │   ├── SyncPanel.tsx         # 同步控制面板
│   │   │   └── VideoTable.tsx        # 视频列表卡片
│   │   └── types/index.ts            # TypeScript 类型定义
│   ├── vite.config.ts                # Vite 配置
│   └── package.json                  # 前端依赖
├── start.bat                         # 一键启动脚本
├── login.bat                         # 登录脚本
└── AGENTS.md                         # 开发指南
```

---

## 3. 后端架构详解

### 3.1 入口与生命周期

#### main.py - FastAPI 主入口

**文件**: [main.py](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/backend/app/main.py)

**核心职责**:
- 创建 FastAPI 应用实例
- 配置 CORS 中间件（允许 5173/3000 端口跨域）
- 注册 API 路由聚合
- SPA 静态文件服务（生产模式）
- 应用生命周期管理

**关键函数**:

| 函数 | 说明 |
|------|------|
| `lifespan(app)` | 异步上下文管理器，启动时初始化目录/日志/数据库，关闭时释放资源 |
| `serve_spa(full_path)` | SPA 路由 fallback，包含路径穿越防护和 API 路径排除 |

**启动链路**:
```
lifespan 启动
  → ensure_dirs()       # 确保数据目录存在
  → setup_debug_logging()  # 初始化环形缓冲区日志
  → setup_sync_logger()    # 初始化同步文件日志
  → init_db()           # 数据库连接 + 建表
  → yield (服务运行中)
  → close_db()          # 关闭数据库连接
```

#### run_server.py - 启动脚本

**文件**: [run_server.py](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/backend/run_server.py)

**关键设计**:
- **必须使用此脚本启动**，不能直接用 `uvicorn`
- 在 uvicorn 加载前设置 `WindowsProactorEventLoopPolicy`
- Playwright 需要 `ProactorEventLoop` 才能创建子进程启动浏览器
- `SelectorEventLoop` 不支持子进程，会静默失败

### 3.2 核心配置层

#### config.py - 统一配置

**文件**: [config.py](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/backend/app/core/config.py)

**路径设计原则**:
- 所有路径基于 `BASE_DIR`（项目根目录）派生
- 禁止硬编码绝对路径
- 通过 `Path(__file__).resolve()` 向上回溯定位根目录

**关键配置项**:

| 配置 | 默认值 | 说明 |
|------|--------|------|
| `BASE_DIR` | 动态计算 | 项目根目录 |
| `DATA_DIR` | `backend/data/` | 运行时数据目录 |
| `AUTH_FILE` | `data/douyin_auth.json` | 登录态文件（storage_state 格式） |
| `DB_FILE` | `data/app.db` | SQLite 数据库文件 |
| `ZHIPUAI_API_KEY` | 从 .env 读取 | 智谱 AI API Key |
| `ZHIPUAI_MODEL` | `glm-4.6v-flash` | AI 模型名称 |
| `DEFAULT_SYNC_LIMIT` | 10 | 默认同步数量 |
| `MAX_SYNC_LIMIT` | 500 | 最大同步数量 |
| `VIDEO_PAGE_TIMEOUT` | 30000ms | 视频详情页加载超时 |
| `BROWSER_ARGS` | [...] | Playwright 反检测参数 |

**关键函数**:

| 函数 | 说明 |
|------|------|
| `ensure_dirs()` | 确保所有必要目录存在（启动时调用） |
| `get_backend_cwd()` | 获取后端工作目录（供启动脚本使用） |

### 3.3 日志系统

#### logger.py - 环形缓冲区日志

**文件**: [logger.py](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/backend/app/core/logger.py)

**核心类**: `RingBufferHandler`

**设计特点**:
- 使用 `collections.deque(maxlen=500)` 实现环形缓冲区
- 保留最近 500 条日志供调试 API 查询
- 线程安全（`threading.Lock`）
- 支持按级别过滤
- 支持 `ai_input` / `ai_output` 自定义属性（AI 调用日志）

**日志条目格式**:
```python
{
    "time": "2026-06-28T14:30:00.000",
    "level": "INFO",
    "logger": "app.services.ai_service",
    "message": "[TEXT] 摘要 150字 | 分类 技术/编程",
    "ai_input": {...},   // 可选
    "ai_output": {...},  // 可选
}
```

**关键函数**:

| 函数 | 说明 |
|------|------|
| `setup_debug_logging()` | 初始化环形缓冲区日志处理器（全局只调用一次） |
| `get_recent_logs(n, min_level)` | 获取最近 N 条日志（按级别过滤） |

### 3.4 数据库层

#### database.py - SQLite 异步连接

**文件**: [database.py](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/backend/app/db/database.py)

**设计特点**:
- 使用 `aiosqlite` 实现异步数据库操作
- 单例模式管理数据库连接
- 健康检查机制：连接失效时自动重连
- WAL 模式（提高并发读写性能）
- 启用外键约束

**数据库表**:

**videos 表**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| url | TEXT UNIQUE | 视频 URL（唯一约束，用于去重） |
| title | TEXT | 视频标题 |
| author | TEXT | 作者名称 |
| author_id | TEXT | 作者 ID |
| desc | TEXT | 视频描述 |
| summary | TEXT | AI 生成的摘要 |
| category | TEXT | AI 分类 |
| tags | TEXT (JSON) | 标签数组（JSON 序列化） |
| key_points | TEXT (JSON) | 关键点数组 |
| quality_score | REAL | 质量评分 |
| cover_url | TEXT | 封面图片 URL |
| cover_path | TEXT | 本地封面路径 |
| scraped_at | TEXT | 抓取时间 |
| created_at | TEXT | 创建时间（默认当前时间） |
| updated_at | TEXT | 更新时间 |

**sync_tasks 表**:
| 字段 | 类型 | 说明 |
|------|------|------|
| task_id | TEXT PK | 任务 ID |
| status | TEXT | 状态：running/completed/failed/cancelled |
| progress | INTEGER | 进度百分比 0-100 |
| current_title | TEXT | 当前处理的视频标题 |
| error | TEXT | 错误信息 |
| started_at | TEXT | 开始时间 |
| finished_at | TEXT | 结束时间 |

**索引**:
- `idx_videos_url` - 视频 URL 索引
- `idx_videos_category` - 分类索引

**关键函数**:

| 函数 | 说明 |
|------|------|
| `get_db()` | 获取数据库连接（单例 + 健康检查） |
| `init_db()` | 初始化数据库表结构 |
| `close_db()` | 关闭数据库连接 |
| `_create_tables(db)` | 创建所有数据表和索引 |

### 3.5 数据模型层

#### video.py - Pydantic 模型

**文件**: [video.py](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/backend/app/models/video.py)

**模型层次**:

```
VideoBase (基础字段)
  ├── VideoCreate (创建模型，含 scraped_at)
  ├── VideoUpdate (更新模型，所有字段可选)
  └── VideoDB (数据库模型，含 id/created_at/updated_at)
       └── VideoResponse (API 响应模型)
```

**模型说明**:

| 模型 | 用途 | 关键特性 |
|------|------|----------|
| `VideoBase` | 字段定义基类 | 包含 url, title, author, desc, summary, category 等 |
| `VideoCreate` | 创建视频时 | 含 scraped_at 字段（默认当前时间） |
| `VideoUpdate` | 更新视频时 | 所有字段 Optional，支持部分更新 |
| `VideoDB` | 数据库行映射 | `from_attributes=True` 支持 ORM 模式 |
| `VideoResponse` | API 响应 | 继承 VideoDB，目前等价 |
| `VideoListResponse` | 列表响应 | 含 items 和 total 字段 |

### 3.6 数据仓库层

#### video_repo.py - 视频数据仓库

**文件**: [video_repo.py](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/backend/app/repositories/video_repo.py)

**安全设计**:
- **列名白名单** (`ALLOWED_COLUMNS`)：防止 SQL 注入
- 更新时只允许修改白名单内的列
- 非法列名被静默忽略（不抛出错误）

**容错设计**:
- `_safe_json_loads()`：安全的 JSON 解析，脏数据不崩溃
- tags/key_points 字段存储为 JSON 字符串，读取时安全解析

**关键函数**:

| 函数 | 说明 |
|------|------|
| `create_video(video)` | 创建视频（URL 已存在则返回现有记录） |
| `get_video_by_id(id)` | 根据 ID 获取视频 |
| `get_video_by_url(url)` | 根据 URL 获取视频 |
| `get_videos(limit, offset, category)` | 获取视频列表（分页 + 分类筛选） |
| `get_videos_count(category)` | 获取视频总数 |
| `get_existing_urls()` | 获取所有已存在 URL（用于去重，返回 Set） |
| `update_video(id, **kwargs)` | 更新视频（白名单过滤） |
| `delete_video(id)` | 删除单个视频 |
| `delete_videos(ids)` | 批量删除视频（返回删除数量） |
| `get_categories()` | 获取所有分类（DISTINCT） |
| `_row_to_video(row)` | 数据库行 → VideoDB 对象转换 |

#### task_repo.py - 任务状态仓库

**文件**: [task_repo.py](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/backend/app/repositories/task_repo.py)

**安全设计**:
- `ALLOWED_TASK_COLUMNS` 白名单：防止 SQL 注入
- 非法列名抛出 `ValueError`（严格模式）

**关键函数**:

| 函数 | 说明 |
|------|------|
| `create_task(task_id)` | 创建新任务 |
| `get_task(task_id)` | 获取任务状态 |
| `get_running_task()` | 获取当前正在运行的任务（最多一个） |
| `update_task(task_id, **kwargs)` | 更新任务（白名单过滤） |
| `complete_task(task_id)` | 标记任务完成（status=completed, progress=100） |
| `fail_task(task_id, error)` | 标记任务失败 |
| `get_recent_tasks(limit)` | 获取最近的任务记录 |

### 3.7 爬虫层

#### auth_manager.py - 登录态管理

**文件**: [auth_manager.py](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/backend/app/scraper/auth_manager.py)

**核心原则**:
- 只保存 `storage_state`（包含 cookies + localStorage）
- **禁止只保存 cookies**（抖音登录态可能存储在 localStorage 中）
- 文件格式：Playwright `storage_state` JSON

**异常类**:

| 异常 | 说明 |
|------|------|
| `AuthError` | 登录态相关错误基类 |
| `AuthFileNotFoundError` | 登录态文件不存在（继承 AuthError） |

**关键函数**:

| 函数 | 说明 |
|------|------|
| `run_login_flow()` | 人工扫码登录流程（有头浏览器） |
| `_verify_login_state(page)` | 验证页面登录状态（检查页面内容） |
| `load_auth_context(browser)` | 加载登录态到浏览器上下文 |
| `is_auth_exists()` | 检查登录态文件是否存在 |
| `delete_auth()` | 删除登录态文件（退出登录） |
| `get_auth_file_path()` | 获取登录态文件路径 |

**登录流程**:
```
启动有头浏览器 → 访问抖音首页 → 用户扫码登录 → 按回车确认
  → 验证登录状态 → 保存 storage_state 到文件 → 关闭浏览器
```

#### sync_engine.py - 同步引擎

**文件**: [sync_engine.py](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/backend/app/scraper/sync_engine.py)

**核心原则**: 只读、无头、容错

**异常类**: `SyncError` - 同步相关错误

**关键函数**:

| 函数 | 说明 |
|------|------|
| `setup_sync_logger()` | 设置同步专用文件日志器（启动时调用） |
| `fetch_favorites(limit, existing_urls)` | 异步生成器，拉取收藏列表 |
| `fetch_favorites_list(limit, existing_urls)` | 返回完整列表的封装版本 |
| `fetch_favorites_enriched(limit, existing_urls)` | 增强版：列表 + 详情页完整描述 + 视频源 |
| `extract_video_page_info(page, url)` | 提取视频详情页信息（完整 desc + video_src_url） |
| `_extract_video_info(item)` | 从列表元素提取视频基础信息 |
| `_navigate_to_favorites(page)` | 导航到收藏页面 |
| `_is_noise_text(text)` | 检测无意义的播放器 UI 文本 |

**播放器 UI 文本过滤** (`_is_noise_text`):
- 过滤包含时间格式的文本（如 `00:00 / 03:45`）
- 过滤含多个播放器关键词的文本（倍速、清屏、连播、章节要点）
- 过滤过短的文本（< 15 字符）
- 过滤错误页面关键词（页面不见了、已被删除等）

**增强版同步流程**:
```
启动无头浏览器 → 加载登录态 → 进入收藏页面 → 滚动加载列表
  → 对每个新视频:
      → 打开新标签页访问详情页
      → 提取完整描述（过滤 UI 噪声）
      → 提取视频源地址
      → 关闭详情页
  → 返回 enriched 视频列表
```

#### selectors.py - CSS 选择器管理

**文件**: [selectors.py](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/backend/app/scraper/selectors.py)

**设计原则**:
- 抖音 DOM 结构频繁变化，选择器集中管理便于更新
- 使用多选择器 fallback 策略，提高容错性
- 优先使用特定选择器，兜底用通用选择器

**选择器分类**:

| 分类 | 说明 |
|------|------|
| `VIDEO_LIST_SELECTORS` | 收藏页视频列表容器 |
| `VIDEO_LINK_SELECTORS` | 视频链接元素 |
| `VIDEO_TITLE_SELECTORS` | 视频标题（优先 img alt 属性） |
| `VIDEO_DESC_SELECTORS` | 视频列表页描述 |
| `VIDEO_COVER_SELECTORS` | 视频封面图片 |
| `VIDEO_DESC_DETAIL_SELECTORS` | 详情页完整描述（避免匹配播放器 UI） |
| `VIDEO_SOURCE_SELECTORS` | 视频源地址 |
| `VIDEO_PAGE_ERROR_KEYWORDS` | 错误页面关键词 |
| `VIDEO_PAGE_NOISE_KEYWORDS` | 播放器 UI 噪声关键词 |
| `FAVORITE_TAB_SELECTORS` | 收藏标签按钮 |

### 3.8 业务服务层

#### sync_service.py - 同步任务服务

**文件**: [sync_service.py](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/backend/app/services/sync_service.py)

**核心设计**: 同步任务在**独立线程**中运行

**为什么需要独立线程**:
- uvicorn 的事件循环与 Playwright 子进程可能冲突
- `ProactorEventLoopPolicy` 只在主线程设置不够
- 热重载（reload）后的 worker 进程可能丢失策略设置
- 独立线程 + 独立事件循环 = 可靠运行

**全局状态**:
- `_current_thread`: 当前运行的线程引用
- `_stop_event`: 停止信号（`threading.Event`）

**关键函数**:

| 函数 | 说明 |
|------|------|
| `start_sync(task_id, limit)` | 启动同步任务（创建独立线程） |
| `cancel_sync(task_id)` | 取消同步任务（设置停止信号） |
| `get_task_status(task_id)` | 获取任务状态 |
| `get_running_task()` | 获取当前运行的任务 |
| `_run_sync_in_thread(task_id, limit)` | 线程入口函数（创建独立事件循环） |
| `_run_sync_task(task_id, limit)` | 实际同步逻辑（async） |

**同步任务流程**:
```
start_sync()
  → 检查是否有运行中的任务
  → 创建任务记录（status=running）
  → 启动独立线程
    → 线程内设置 ProactorEventLoopPolicy
    → 创建新的 asyncio 事件循环
    → 执行 _run_sync_task()
      → fetch_favorites_enriched(limit)  抓取视频
      → 对每个新视频:
          → 检查停止信号
          → generate_summary_and_category()  AI 总结+分类
          → video_repo.create_video()  存入数据库
          → 更新任务进度
      → complete_task() 标记完成
      → 异常处理：AuthError / SyncError / Exception
```

#### ai_service.py - AI 服务

**文件**: [ai_service.py](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/backend/app/services/ai_service.py)

**AI 模型**: `glm-4.6v-flash`（智谱免费多模态模型）

**双路由策略**:

| 模式 | 触发条件 | 超时 | 说明 |
|------|----------|------|------|
| TEXT 模式 | desc >= 50 字 | 30s | 纯文本模式，基于标题+描述生成总结 |
| VL 模式 | desc < 50 字 且 有 video_url | 120s | 视频理解模式，分析视频画面内容 |
| Fallback | API Key 缺失或调用失败 | - | 直接截取描述/标题 |

**thinking 设置**: `thinking: {"type": "disabled"}`
- 输出走 `content` 字段（稳定可控）
- `reasoning_content` 做兜底

**预设分类** (12 个):
```
技术/编程、生活vlog、美食、旅行、游戏、搞笑、
知识/教育、音乐、运动健身、美妆时尚、影视、其他
```

**System Prompt 要求**:
1. 总结必须基于实际内容，禁止重复标题和描述
2. 100-200 字，结构清晰，包含内容概述、要点和价值
3. 最后选择最匹配的分类，格式：`【分类：xxx】`

**关键函数**:

| 函数 | 说明 |
|------|------|
| `generate_summary_and_category(title, desc, video_url)` | 生成摘要和分类（主入口） |
| `generate_summary(title, desc, video_url)` | 只生成摘要（便捷函数） |
| `_parse_response(raw)` | 解析模型输出 → (summary, category) |
| `_extract_summary(text)` | 从模型输出提取总结段落（5 级 fallback 策略） |
| `_match_category(text)` | 从文本中匹配分类（全文扫描 + 关键词映射） |
| `_fallback_summary(title, desc)` | 兜底摘要（直接截取） |
| `_looks_like_player_ui(text)` | 检测播放器 UI 文本（二次防护） |

**摘要提取策略**（按优先级）:
1. 按 `【分类：xxx】` 分割，取之前的内容
2. 中文引号（「」/""）内的长文本
3. 英文引号内的长文本
4. 最后一个非序号开头的段落
5. 最后一句完整的中文句子

**限流处理**:
- 免费模型可能遇到 429 频率限制
- 自动退化到描述截取 fallback
- 详细错误记录在调试日志中

### 3.9 API 层

#### 路由聚合

**文件**: [__init__.py](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/backend/app/api/v1/__init__.py)

**路由挂载**:
- `/health` → health_router
- `/api/videos/*` → videos_router
- `/api/sync/*` → sync_router
- `/api/auth/*` → auth_router
- `/api/debug/*` → debug_router

#### health.py - 健康检查

**文件**: [health.py](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/backend/app/api/v1/health.py)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 返回服务状态和登录态是否存在 |

#### videos.py - 视频管理

**文件**: [videos.py](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/backend/app/api/v1/videos.py)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/videos` | 视频列表（?limit=&offset=&category=） |
| GET | `/api/videos/categories` | 分类列表 |
| GET | `/api/videos/{id}` | 单个视频详情 |
| PUT | `/api/videos/{id}` | 更新视频信息 |
| DELETE | `/api/videos/{id}` | 删除单个视频 |
| POST | `/api/videos/delete-batch` | 批量删除（body: {ids: [...]}） |

#### sync.py - 同步任务

**文件**: [sync.py](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/backend/app/api/v1/sync.py)

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/sync/start` | 启动同步（?limit=，0 表示全部） |
| POST | `/api/sync/stop` | 停止同步（?task_id= 可选） |
| GET | `/api/sync/status/{task_id}` | SSE 实时进度推送 |

**SSE 超时**: 30 分钟（`SSE_TIMEOUT_SECONDS = 1800`）

#### auth.py - 认证管理

**文件**: [auth.py](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/backend/app/api/v1/auth.py)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/auth/status` | 获取登录状态 |
| POST | `/api/auth/logout` | 退出登录（删除登录态文件） |

#### debug.py - 调试日志

**文件**: [debug.py](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/backend/app/api/v1/debug.py)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/debug/logs` | 获取最近日志（?n=100&level=INFO） |

---

## 4. 前端架构详解

### 4.1 技术栈

- **框架**: React 19.2.6 + TypeScript 6.0
- **构建工具**: Vite 8.0.12
- **样式**: Tailwind CSS v4（`@tailwindcss/vite` 插件）
- **路由**: react-router-dom 7.16.0（已安装但当前版本未深度使用）

### 4.2 目录结构

```
frontend/src/
├── main.tsx           # 应用入口
├── App.tsx            # 主应用组件（状态管理中心）
├── index.css          # 全局样式 + Tailwind 指令
├── api/
│   └── client.ts      # API 客户端封装
├── hooks/
│   └── useSync.ts     # 同步状态 Hook (SSE)
├── components/
│   ├── Layout.tsx     # 布局组件（导航栏 + 内容区）
│   ├── SyncPanel.tsx  # 同步控制面板
│   └── VideoTable.tsx # 视频卡片列表
└── types/
    └── index.ts       # TypeScript 类型定义
```

### 4.3 核心组件

#### App.tsx - 主应用

**文件**: [App.tsx](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/frontend/src/App.tsx)

**状态管理**:
- `backendOk`: 后端服务是否可用
- `authExists`: 登录态是否存在
- `videos`: 视频列表数据
- `categories`: 分类列表
- `selectedCategory`: 当前选中的分类
- `loading`: 加载中状态

**初始化流程**:
```
useEffect 挂载
  → checkHealth() 检查后端健康状态
  → 并行: getVideos() + getCategories()
  → 更新状态，结束加载
```

#### Layout.tsx - 布局组件

**文件**: [Layout.tsx](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/frontend/src/components/Layout.tsx)

**结构**:
- 顶部导航栏（标题 + 退出登录按钮）
- 内容区域（最大宽度 7xl，居中）

#### SyncPanel.tsx - 同步控制面板

**文件**: [SyncPanel.tsx](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/frontend/src/components/SyncPanel.tsx)

**功能**:
- 同步数量选择（10/30/50/全部）
- 开始/停止同步按钮
- 登录态缺失提示
- 同步消息展示（成功/失败/进行中）
- 进度条 + 当前处理视频标题

#### VideoTable.tsx - 视频列表

**文件**: [VideoTable.tsx](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/frontend/src/components/VideoTable.tsx)

**功能**:
- 分类筛选标签（全部 + 各分类）
- 全选 / 多选 checkbox
- 批量删除
- 视频卡片展示（封面 + 标题 + 摘要 + 作者）
- 标题展开/收起（长标题）
- 封面加载失败降级（显示 🎬 图标）
- 下载 Markdown
- 打开原视频（新标签页）
- 单个删除

### 4.4 自定义 Hook

#### useSync.ts - 同步状态管理

**文件**: [useSync.ts](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/frontend/src/hooks/useSync.ts)

**SyncState 接口**:
```typescript
interface SyncState {
  taskId: string | null;
  status: 'idle' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  currentTitle: string;
  error: string | null;
  message: string;
}
```

**核心功能**:
- 启动同步（调用 API + 创建 SSE 连接）
- 停止同步（调用 API + 关闭 SSE）
- SSE 实时进度更新
- 连接断开自动标记失败
- 组件卸载自动清理 SSE 连接
- 完成回调通知

**返回值**:
```typescript
{
  ...state,       // 所有状态字段
  start,          // 启动函数 (limit) => Promise<void>
  stop,           // 停止函数 () => Promise<void>
  isRunning,      // 便捷计算属性
}
```

### 4.5 API 客户端

#### client.ts - API 封装

**文件**: [client.ts](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/frontend/src/api/client.ts)

**设计原则**:
- 使用 Vite proxy，相对路径即可（无需硬编码后端地址）
- 统一错误处理（非 2xx 抛出 Error）
- TypeScript 泛型类型支持

**核心函数**:

| 函数 | 方法 | 路径 | 说明 |
|------|------|------|------|
| `checkHealth()` | GET | `/health` | 健康检查 |
| `getVideos(limit, offset, category)` | GET | `/api/videos` | 视频列表 |
| `getCategories()` | GET | `/api/videos/categories` | 分类列表 |
| `startSync(limit)` | POST | `/api/sync/start` | 启动同步 |
| `stopSync(taskId?)` | POST | `/api/sync/stop` | 停止同步 |
| `createSyncSSE(taskId, onMessage, onError)` | - | `/api/sync/status/{id}` | 创建 SSE 连接 |
| `logout()` | POST | `/api/auth/logout` | 退出登录 |
| `deleteVideo(id)` | DELETE | `/api/videos/{id}` | 删除单个视频 |
| `deleteVideos(ids)` | POST | `/api/videos/delete-batch` | 批量删除 |

### 4.6 类型定义

**文件**: [types/index.ts](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/frontend/src/types/index.ts)

**主要类型**:
- `Video` - 视频数据类型
- `VideoListResponse` - 视频列表响应
- `SyncTask` - 同步任务
- `CategoryDistribution` - 分类分布
- `Stats` - 统计信息（规划中）
- `SearchResult` - 搜索结果（规划中）
- `AuthStatus` - 认证状态
- `HealthStatus` - 健康状态

---

## 5. 核心数据模型

### 5.1 视频数据流转

```
抖音页面 (HTML)
  ↓ Playwright 提取
ScrapedVideo (dict)
  ↓ AI 总结 + 分类
VideoCreate (Pydantic)
  ↓ video_repo.create_video()
SQLite Row (aiosqlite.Row)
  ↓ _row_to_video()
VideoDB (Pydantic)
  ↓ API 响应
VideoResponse (Pydantic) → JSON → Video (TS)
```

### 5.2 同步任务状态流转

```
           start_sync()
               ↓
          [running] ←────────┐
               │              │
         进度更新中           │ 停止信号
               │              │
    ┌──────────┼──────────┐   │
    ↓          ↓          ↓   │
[completed] [failed] [cancelled]
    ↑          ↑          ↑
    └──────────┴──────────┘
         终态（不可逆转）
```

---

## 6. API 接口文档

### 6.1 健康检查

#### GET /health

获取后端服务健康状态和登录态信息。

**响应示例**:
```json
{
  "status": "ok",
  "auth_exists": true
}
```

### 6.2 视频管理

#### GET /api/videos

获取视频列表，支持分页和分类筛选。

**查询参数**:
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| limit | int | 100 | 每页数量 |
| offset | int | 0 | 偏移量 |
| category | string | - | 分类筛选（可选） |

**响应示例**:
```json
{
  "items": [
    {
      "id": 1,
      "url": "https://www.douyin.com/video/xxx",
      "title": "视频标题",
      "author": "作者名",
      "desc": "视频描述",
      "summary": "AI 生成的摘要...",
      "category": "技术/编程",
      "cover_url": "https://...",
      "tags": [],
      "key_points": [],
      "quality_score": 0,
      "scraped_at": "2026-06-28T10:00:00",
      "created_at": "2026-06-28T10:00:00",
      "updated_at": "2026-06-28T10:00:00"
    }
  ],
  "total": 42
}
```

#### GET /api/videos/categories

获取所有分类列表。

**响应示例**:
```json
{
  "categories": ["技术/编程", "生活vlog", "美食"]
}
```

#### GET /api/videos/{id}

获取单个视频详情。

#### PUT /api/videos/{id}

更新视频信息。

**请求体**: `VideoUpdate`（所有字段可选）

#### DELETE /api/videos/{id}

删除单个视频。

#### POST /api/videos/delete-batch

批量删除视频。

**请求体**:
```json
{
  "ids": [1, 2, 3]
}
```

### 6.3 同步任务

#### POST /api/sync/start

启动同步任务。

**查询参数**:
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| limit | int | 0 | 同步数量（0 表示全部，上限 500） |

**响应示例**:
```json
{
  "task_id": "sync_a1b2c3d4",
  "status": "running",
  "message": "同步任务已启动"
}
```

**错误响应**:
- `401`: 未登录
- `409`: 已有任务在运行

#### POST /api/sync/stop

停止同步任务。

**查询参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| task_id | string | 任务 ID（可选，不传则停止当前运行的任务） |

#### GET /api/sync/status/{task_id}

SSE 实时推送同步进度。

**事件格式**（每行一条，以 `data: ` 开头）:
```
data: {"task_id":"sync_xxx","status":"running","progress":30,"current_title":"视频标题","error":null}

data: {"type":"done","status":"completed"}
```

**状态值**: `running` / `completed` / `failed` / `cancelled`

### 6.4 认证管理

#### GET /api/auth/status

获取登录状态。

**响应示例**:
```json
{
  "logged_in": true,
  "message": "已登录"
}
```

#### POST /api/auth/logout

退出登录（删除登录态文件）。

### 6.5 调试日志

#### GET /api/debug/logs

获取最近的调试日志。

**查询参数**:
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| n | int | 100 | 返回条数（1-500） |
| level | string | DEBUG | 最低日志级别 |

---

## 7. 关键流程说明

### 7.1 首次使用流程

```
用户首次启动
  → start.bat
    → 检查 venv，不存在则创建
    → 安装 Python 依赖
    → 安装 Playwright 浏览器
    → 检查 node_modules，不存在则安装
    → 启动后端 + 前端
  → 用户打开 http://localhost:5173
  → 提示未登录
  → 运行 login.bat (login_manual.py)
    → 打开有头浏览器
    → 用户扫码登录
    → 按回车保存登录态
  → 刷新前端页面
  → 点击"开始同步"
  → 等待同步完成
  → 浏览视频列表
```

### 7.2 同步任务完整流程

```
前端点击"开始同步"
  ↓
POST /api/sync/start
  ↓
sync_service.start_sync()
  ├─ 检查是否有运行中的任务
  ├─ 创建 task 记录（running）
  └─ 启动独立线程
       ↓
  _run_sync_in_thread()
    ├─ 设置 ProactorEventLoopPolicy
    ├─ 创建新事件循环
    └─ _run_sync_task()
         ├─ fetch_favorites_enriched(limit)
         │   ├─ 启动无头浏览器
         │   ├─ 加载登录态
         │   ├─ 导航到收藏页
         │   └─ 滚动抓取 + 详情页提取
         ├─ 获取 existing_urls（去重）
         └─ 对每个新视频:
              ├─ 检查停止信号
              ├─ generate_summary_and_category()
              │   ├─ 判断 TEXT/VL 模式
              │   ├─ 调用 GLM API
              │   └─ 解析响应 → (summary, category)
              ├─ video_repo.create_video()
              └─ 更新任务进度
                   ↓
              完成 / 失败 / 取消
                   ↓
              更新 task 状态（终态）
```

### 7.3 AI 双路由决策流程

```
输入: title, desc, video_url
  ↓
API Key 是否存在?
  ├─ 否 → 返回 fallback 摘要 + "未分类"
  └─ 是 → 继续
       ↓
  desc 是否是播放器 UI 文本?
    ├─ 是 → 清空 desc
    └─ 否 → 保持
         ↓
    desc 长度 >= 50?
      ├─ 是 → TEXT 模式（标题+描述）
      └─ 否 → 有 video_url?
           ├─ 是 → VL 模式（视频理解）
           └─ 否 → TEXT 模式（仅标题）
```

---

## 8. 配置与环境

### 8.1 环境变量

**文件**: `backend/.env`（从 `.env.example` 复制）

| 变量 | 说明 | 必填 |
|------|------|------|
| `ZHIPUAI_API_KEY` | 智谱 AI API Key | 是（AI 功能） |
| `ZHIPUAI_BASE_URL` | 智谱 API 基础 URL | 否（默认官方地址） |
| `ZHIPUAI_MODEL` | 使用的模型名称 | 否（默认 glm-4.6v-flash） |

### 8.2 数据目录

**路径**: `backend/data/`

| 文件/目录 | 说明 |
|-----------|------|
| `app.db` | SQLite 数据库文件 |
| `app.db-wal` | WAL 模式预写日志 |
| `app.db-shm` | WAL 共享内存文件 |
| `douyin_auth.json` | 抖音登录态（storage_state） |
| `logs/sync.log` | 同步日志文件 |
| `logs/sync_error.log` | 同步错误日志 |

### 8.3 Vite 代理配置

前端开发服务器通过 Vite proxy 转发 API 请求到后端，避免跨域问题。

（具体配置见 `vite.config.ts`）

---

## 9. 开发与运行

### 9.1 快速启动

```bat
start.bat    # 一键启动（自动创建 venv、安装依赖、启动前后端）
login.bat    # 首次抖音登录
```

### 9.2 后端开发命令

```bash
cd backend

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器（首次）
playwright install chromium

# 启动后端服务（必须用 run_server.py）
python run_server.py

# 手动登录
python login_manual.py

# 同步测试（拉取 1 条）
python test_sync.py

# 环境诊断
python diagnose.py
```

### 9.3 前端开发命令

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 代码检查
npm run lint
```

### 9.4 端口说明

| 服务 | 端口 | 说明 |
|------|------|------|
| 后端 API | 8000 | FastAPI + Uvicorn |
| 前端开发 | 5173 | Vite Dev Server |
| API 文档 | 8000/docs | Swagger UI |

### 9.5 生产部署

1. 前端构建: `cd frontend && npm run build`
2. 后端启动: `cd backend && python run_server.py`
3. 访问 `http://localhost:8000`（后端自动托管前端静态文件）

---

## 10. 已知问题与注意事项

### 10.1 Windows asyncio 兼容性

**问题**: Playwright 需要 `ProactorEventLoop` 才能创建子进程启动浏览器。

**解决方案**:
- 必须通过 `run_server.py` 启动后端
- 不能直接用 `uvicorn app.main:app`
- 同步任务在独立线程中运行，确保事件循环正确
- `main.py` 也设置了事件循环策略作为热重载保险

### 10.2 热重载可能崩溃

**问题**: WatchFiles reload 有时会杀死子进程导致后端不响应。

**解决方案**:
```powershell
Stop-Process -Name python -Force
# 然后重新启动
```

### 10.3 抖音页面结构变化

**问题**: 抖音 DOM 结构频繁变化，可能导致选择器失效。

**解决方案**:
- 所有 CSS 选择器集中在 `selectors.py` 管理
- 使用多选择器 fallback 策略
- 如果抓取失败，更新对应选择器

### 10.4 登录态过期

**问题**: Cookie 约 7 天失效，同步时报认证错误。

**解决方案**: 重新运行 `login_manual.py` 扫码登录。

### 10.5 播放器 UI 文本污染

**问题**: 视频详情页抓取时可能误将播放器 UI 文本（倍速、清屏、时间戳等）当作视频描述。

**解决方案**:
- `_is_noise_text()` 函数检测并过滤
- 时间格式正则匹配（`XX:XX / XX:XX`）
- 播放器关键词检测（倍速、清屏、连播、章节要点）
- AI 服务中做二次防护（`_looks_like_player_ui`）

### 10.6 AI 限流

**问题**: 免费模型（glm-4.6v-flash）有频率限制，可能返回 429。

**解决方案**:
- 自动退化到描述截取 fallback
- 详细错误记录在调试日志中
- 可通过 `/api/debug/logs` 查看

### 10.7 VL 模式效果

**问题**: VL 模式用 GLM-4.6V-Flash 分析视频 URL，效果取决于模型能否访问 Douyin CDN。

**替代方案**: 本地 VL 模型（用户有 RTX 4060），可考虑 Ollama + Qwen3-VL-2B q4 量化。

### 10.8 没有自动化测试

**问题**: `backend/test_*.py` 是手动诊断脚本，不是 pytest 测试套件，没有 CI/CD。

---

## 附录：文件索引

### 后端核心文件

| 文件 | 职责 |
|------|------|
| [main.py](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/backend/app/main.py) | FastAPI 入口 + 生命周期 |
| [run_server.py](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/backend/run_server.py) | 启动脚本（Windows 兼容） |
| [config.py](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/backend/app/core/config.py) | 全局配置 + 路径管理 |
| [logger.py](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/backend/app/core/logger.py) | 环形缓冲区日志系统 |
| [database.py](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/backend/app/db/database.py) | SQLite 异步连接 |
| [video.py](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/backend/app/models/video.py) | 视频数据模型 |
| [video_repo.py](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/backend/app/repositories/video_repo.py) | 视频数据仓库 |
| [task_repo.py](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/backend/app/repositories/task_repo.py) | 任务状态仓库 |
| [auth_manager.py](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/backend/app/scraper/auth_manager.py) | 登录态管理 |
| [sync_engine.py](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/backend/app/scraper/sync_engine.py) | 同步引擎（Playwright） |
| [selectors.py](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/backend/app/scraper/selectors.py) | CSS 选择器集中管理 |
| [sync_service.py](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/backend/app/services/sync_service.py) | 同步任务服务（独立线程） |
| [ai_service.py](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/backend/app/services/ai_service.py) | AI 总结 + 分类 |

### 前端核心文件

| 文件 | 职责 |
|------|------|
| [App.tsx](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/frontend/src/App.tsx) | 主应用组件 |
| [client.ts](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/frontend/src/api/client.ts) | API 客户端封装 |
| [useSync.ts](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/frontend/src/hooks/useSync.ts) | 同步状态 Hook |
| [Layout.tsx](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/frontend/src/components/Layout.tsx) | 布局组件 |
| [SyncPanel.tsx](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/frontend/src/components/SyncPanel.tsx) | 同步控制面板 |
| [VideoTable.tsx](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/frontend/src/components/VideoTable.tsx) | 视频列表卡片 |
| [index.ts](file:///c:/Users/Ibuprofen/Desktop/MU.X.Y/05_项目/dy_cliprepo/frontend/src/types/index.ts) | TypeScript 类型定义 |

---

*文档生成时间: 2026-06-28*
*项目版本: 1.0.0-mvp*
