# 抖音收藏 AI 知识库 - 实现计划书

> 版本：v1.0 | 日期：2026-06-02 | 状态：已确认

---

## 一、项目概述

### 1.1 项目名称
抖音收藏 AI 知识库（Douyin Knowledge Base）

### 1.2 项目目标
构建一个本地私有化知识管理工具，自动抓取抖音收藏视频，通过 AI 进行智能总结、分类和标签提取，构建可检索的结构化知识库。

### 1.3 核心理念
「收藏不等于拥有，检索才能创造价值。」

---

## 二、技术架构

### 2.1 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        前端 (Frontend)                       │
│  React 18 + TypeScript + Tailwind + Shadcn/ui              │
│  - 收藏同步控制台                                           │
│  - AI 总结看板（分类/标签/时间轴）                           │
│  - 语义搜索引擎                                             │
│  - 视频播放器嵌入                                           │
└──────────────────────────┬──────────────────────────────────┘
                         │  HTTP (FastAPI)
┌──────────────────────────▼──────────────────────────────────┐
│                        后端 (Backend)                        │
│  Python FastAPI + SQLite + ChromaDB                         │
│  - Playwright 数据采集服务                                   │
│  - AI 处理管道 (Ollama/DeepSeek/OpenAI)                     │
│  - 向量检索引擎                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **前端** | React 18 + TypeScript + Tailwind CSS | 现代化UI框架，响应式设计 |
| **后端** | Python FastAPI | 异步高性能，支持 SSE |
| **数据库** | SQLite + ChromaDB | 结构化存储 + 向量检索 |
| **AI层** | Ollama / OpenAI / DeepSeek | 支持本地和云端模型 |
| **自动化** | Playwright | 浏览器自动化抓取 |

### 2.3 数据流

```
Playwright 抓取 → AI 总结与向量化 → SQLite + ChromaDB → React 可视化
```

---

## 三、功能特性

| 能力 | 说明 |
|------|------|
| 一键同步 | 自动登录抖音网页版，抓取收藏列表，支持断点续传 |
| AI 智能总结 | 自动生成视频核心要点、干货评分 |
| 自动分类 | 归类到编程技术/商业思维/生活技巧/心理学等维度 |
| 语义搜索 | 基于向量的自然语言搜索 |
| 私有化部署 | 全部本地运行，数据不出境 |
| 现代化看板 | 分类浏览、时间轴、标签云、质量筛选 |

---

## 四、目录结构

```
dy_cliprepo/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── sqlite_manager.py
│   │   │   └── chroma_manager.py
│   │   ├── scraper/
│   │   │   ├── __init__.py
│   │   │   ├── douyin_scraper.py
│   │   │   └── auth_manager.py
│   │   ├── ai/
│   │   │   ├── __init__.py
│   │   │   ├── summarizer.py
│   │   │   ├── embedding.py
│   │   │   └── prompts.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── videos.py
│   │   │   ├── sync.py
│   │   │   ├── search.py
│   │   │   ├── stats.py
│   │   │   └── auth.py
│   │   └── services/
│   │       ├── __init__.py
│   │       └── sync_service.py
│   ├── auth/
│   ├── data/
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── VideoCard.tsx
│   │   │   ├── CategoryBoard.tsx
│   │   │   ├── SyncProgress.tsx
│   │   │   ├── SearchBar.tsx
│   │   │   └── StatsCards.tsx
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Library.tsx
│   │   │   ├── VideoDetail.tsx
│   │   │   └── Settings.tsx
│   │   ├── hooks/
│   │   │   ├── useSync.ts
│   │   │   └── useSearch.ts
│   │   ├── api/
│   │   │   └── client.ts
│   │   ├── types/
│   │   │   └── index.ts
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
│
├── docs/
├── .gitignore
├── LICENSE
└── README.md
```

---

## 五、分阶段实施计划

### 阶段一：项目骨架搭建（预计 0.5 天）

#### 步骤 1：后端项目初始化
- 创建 `backend/requirements.txt`
- 创建 `backend/.env.example`
- 创建 `backend/app/__init__.py`
- 创建 `backend/app/main.py`（FastAPI 入口 + CORS + 路由挂载）
- 创建 `backend/app/config.py`（配置管理）

#### 步骤 2：前端项目初始化
- 使用 Vite 创建 React + TypeScript 项目
- 安装依赖：axios, react-router-dom, tailwindcss
- 配置 vite.config.ts（proxy 指向后端 :8000）
- 配置 tailwind
- 基础路由：`/`, `/library`, `/video/:id`, `/settings`

#### 步骤 3：.gitignore 配置
- Python 缓存、venv、.env
- Node node_modules、dist
- 数据目录：backend/data/, backend/auth/*.json

### 阶段二：后端数据层（预计 1 天）

#### 步骤 4：数据库模型与管理
- `models.py` - SQLAlchemy ORM 模型（Video 表）
- `sqlite_manager.py` - CRUD 操作
- `chroma_manager.py` - ChromaDB 向量操作

### 阶段三：抓取与AI（预计 2 天）

#### 步骤 5：Playwright 抓取器
- `auth_manager.py` - Cookie 管理
- `douyin_scraper.py` - 抓取核心

#### 步骤 6：AI 处理管道
- `prompts.py` - Prompt 模板
- `summarizer.py` - 多 Provider 支持
- `embedding.py` - 文本向量化

#### 步骤 7：同步服务编排
- `sync_service.py` - 任务管理 + 后台执行

#### 步骤 8：API 路由
- `auth.py`, `sync.py`, `videos.py`, `search.py`, `stats.py`

### 阶段四：前端开发（预计 2-3 天）

#### 步骤 9：前端基础框架
- TypeScript 类型定义
- Axios 封装
- 路由配置

#### 步骤 10：Dashboard 页面
- 统计卡片、分类看板、同步进度

#### 步骤 11：Library + VideoCard
- 视频卡片网格、分类/标签筛选、搜索

#### 步骤 12：VideoDetail + Settings
- 视频详情页、设置页

### 阶段五：集成测试（预计 1-2 天）

#### 步骤 13-15
- 前后端联调
- 异常处理与健壮性
- 端到端测试

---

## 六、API 设计

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/login | 启动扫码登录 |
| GET | /api/auth/status | 检查登录状态 |
| POST | /api/sync/start | 启动同步任务 |
| GET | /api/sync/status | SSE 实时进度 |
| POST | /api/sync/stop | 中止同步 |
| GET | /api/videos | 分页视频列表 |
| GET | /api/videos/:id | 视频详情 |
| POST | /api/search | 语义搜索 |
| GET | /api/stats | 统计数据 |
| POST | /api/ai/regenerate | 重新AI总结 |
| GET | /api/data/export | 导出数据 |
| POST | /api/data/clear | 清空数据 |

---

## 七、数据库 Schema

### SQLite - videos 表

```sql
CREATE TABLE videos (
    id INTEGER PRIMARY KEY,
    url TEXT UNIQUE NOT NULL,
    title TEXT,
    author TEXT,
    author_id TEXT,
    desc TEXT,
    cover_path TEXT,
    summary TEXT,
    category TEXT,
    tags JSON,
    key_points JSON,
    quality_score INTEGER,
    created_at DATETIME,
    favorited_at DATETIME,
    synced_at DATETIME,
    embedding_id TEXT
);
```

### ChromaDB 集合

- Collection: `video_embeddings`
- Documents: `"{title}. {summary}. 标签：{tags}"`
- Metadatas: `{"video_id": 123, "category": "编程技术", "url": "..."}`

---

## 八、关键技术决策

| 决策点 | 选择 | 原因 |
|--------|------|------|
| AI Provider | OpenAI SDK 统一接口 | Ollama/OpenAI/DeepSeek 兼容 |
| 向量数据库 | ChromaDB | 轻量级，无需额外部署 |
| SSE 方案 | sse-starlette | FastAPI 生态最佳支持 |
| 前端状态 | React hooks | 项目规模无需 Redux |
| CSS 方案 | Tailwind CSS | 快速开发 |
| Cookie 存储 | JSON 文件 | 简单直接 |

---

## 九、风险与应对

| 风险 | 应对方案 |
|------|----------|
| 抖音页面结构变化 | 选择器抽取为配置 |
| Playwright 被反爬 | 随机延迟、限速、已登录态 |
| AI 返回非标准 JSON | 正则提取 + 重试 |
| 大量收藏同步耗时 | 断点续传 + 可中止 |
| 视频描述为空 | 降级用标题+作者生成 |

---

## 十、时间估算

| 阶段 | 预计时间 |
|------|----------|
| 阶段一：项目骨架 | 0.5 天 |
| 阶段二：数据层 | 1 天 |
| 阶段三：抓取 + AI + API | 2 天 |
| 阶段四：前端 | 2-3 天 |
| 阶段五：联调测试 | 1-2 天 |
| **总计** | **约 7-9 天** |

---

## 十一、第一个里程碑：最小可运行 Demo

### 目标流程
```
扫码登录 → 抓取收藏 → AI 总结 → 前端展示
```

### 验证标准
1. 用户可通过扫码登录抖音
2. 系统能抓取收藏列表（至少10条）
3. AI 能生成总结、分类、标签
4. 前端能展示视频列表和详情
5. 支持关键词搜索和语义搜索

---

---

## 十二、版本说明与实际实施记录

### 12.1 与原计划的差异

| 项目 | 原计划版本 | 实际版本 | 原因 |
|------|-----------|----------|------|
| ChromaDB | 0.5.0 | >=1.5.0 | 0.5.0 需要编译 C++ 扩展，Windows 环境下安装困难；1.5.x 提供预编译 wheel |

### 12.2 阶段完成状态

| 阶段 | 状态 | 完成日期 | 备注 |
|------|------|----------|------|
| 阶段一：项目骨架 | ✅ 已完成 | 2026-06-02 | 后端 FastAPI + 前端 React |
| 阶段二：数据层验证 | ✅ 已完成 | 2026-06-02 | SQLite + ChromaDB 功能验证通过 |
| 阶段三：抓取 + AI + API | 🔄 进行中 | - | Playwright + AI 管道 |
| 阶段四：前端 | ⏳ 待开始 | - | - |
| 阶段五：联调测试 | ⏳ 待开始 | - | - |

### 12.3 依赖清单（实际）

```
fastapi==0.115.0
uvicorn[standard]==0.30.0
sqlalchemy==2.0.35
chromadb>=1.5.0
playwright==1.48.0
openai==1.50.0
aiofiles==24.1.0
python-dotenv==1.0.0
python-multipart==0.0.12
sse-starlette==2.1.0
pydantic==2.9.0
pydantic-settings==2.5.0
```

---

*计划确认人：用户 | 计划制定日期：2026-06-02*
*最后更新：2026-06-02 | 更新内容：版本差异记录*
