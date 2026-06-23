# 抖音收藏 AI 知识库 (Douyin Knowledge Base)

> 让你的抖音收藏夹从吃灰的仓库，变成可检索、可分类、可复用的个人知识资产。

![版本徽章](https://img.shields.io/badge/version-1.0.0-blue.svg)
![许可证徽章](https://img.shields.io/badge/license-MIT-green.svg)
![Python版本](https://img.shields.io/badge/python-3.11+-yellow.svg)
![Node版本](https://img.shields.io/badge/node-18+-lightgreen.svg)

## 项目简介

这是一个专为重度抖音用户设计的本地私有化知识管理工具。它通过浏览器自动化技术抓取你的抖音收藏视频，利用 AI 对视频内容进行智能总结、自动分类和标签提取，最终构建成一个支持语义搜索的结构化知识库。

所有数据存储在本地，无需担心隐私泄露，也无需依赖抖音官方 API。

**核心理念：「收藏不等于拥有，检索才能创造价值。」**

## 功能特性

| 能力 | 说明 |
|------|------|
| 🔄 一键同步 | 自动登录抖音网页版，抓取收藏列表，支持断点续传和增量更新 |
| 🤖 AI 智能总结 | 基于大语言模型（支持本地 Ollama / 云端 API）自动生成视频核心要点、干货评分 |
| 📁 自动分类体系 | 将杂乱的收藏自动归类到「编程技术 / 商业思维 / 生活技巧 / 心理学」等知识维度 |
| 🔍 语义搜索引擎 | 不是简单的关键词匹配——输入"如何提高专注力"，能搜到相关的心理学和学习方法视频 |
| 🔒 私有化部署 | 前后端完全本地运行，视频数据、AI 处理、向量数据库均不出境 |
| 📊 现代化看板 | React 驱动的可视化界面，支持分类浏览、时间轴、标签云和质量筛选 |

## 技术架构

### 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **前端** | React 19 + TypeScript + Tailwind CSS | 现代化UI框架，响应式设计 |
| **后端** | Python FastAPI | 异步高性能，天然支持 SSE（实时推送同步进度） |
| **数据库** | SQLite + ChromaDB | 结构化存储 + 向量检索，零配置本地部署 |
| **AI层** | Ollama / OpenAI / DeepSeek | 支持本地模型（推荐 Qwen2.5）或云端 API |
| **自动化** | Playwright | 比 Selenium 更现代，能穿透抖音的反爬，且支持保存登录态 |

### 数据流

```
Playwright 抓取 → AI 总结与向量化 → SQLite 结构化存储 + ChromaDB 语义索引 → React 可视化消费
```

## 快速开始

### 环境要求

- **Python**: 3.11 或更高版本
- **Node.js**: 18 或更高版本
- **Git**: 用于克隆仓库
- **操作系统**: Windows 10/11（推荐）

### 方式一：一键启动（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/Ibuprovan/dy_cliprepo.git
cd dy_cliprepo

# 2. 首次登录抖音（只需一次）
login.bat

# 3. 启动服务
start.bat
```

### 方式二：手动启动

#### 后端安装

```bash
# 1. 进入后端目录
cd backend

# 2. 创建Python虚拟环境
python -m venv venv
.\venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 安装Playwright浏览器
playwright install chromium

# 5. 启动后端
python -m uvicorn app.main:app --reload --port 8000
```

#### 前端安装

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖
npm install

# 3. 启动前端
npm run dev
```

### 抖音登录

由于抖音需要登录才能查看收藏，需要先完成扫码登录：

```bash
# 方式一：使用登录脚本
login.bat

# 方式二：手动运行
cd backend
.\venv\Scripts\activate
python -m app.scraper.auth
```

登录成功后，登录态会保存到 `backend/data/auth.json`，后续同步会自动使用。

### AI模型配置

#### 方案A：本地Ollama（推荐，隐私最好）

```bash
# 1. 安装Ollama
# 下载地址：https://ollama.ai

# 2. 拉取模型（中文表现好，14B 在 16G 显存可跑）
ollama pull qwen2.5:14b

# 3. 启动服务
ollama serve
```

#### 方案B：云端API

在 `backend/.env` 中配置：

```env
# 使用 DeepSeek
AI_PROVIDER=deepseek
DEEPSEEK_API_KEY=your-api-key

# 或使用 OpenAI
AI_PROVIDER=openai
OPENAI_API_KEY=your-api-key
```

## 使用说明

### 首次登录

1. 运行 `login.bat` 或执行 `python -m app.scraper.auth`
2. 在弹出的浏览器窗口中使用抖音APP扫码登录
3. 登录成功后，登录态会自动保存

### 同步收藏

1. 启动服务：运行 `start.bat`
2. 打开前端：http://localhost:5173
3. 点击"同步收藏"按钮
4. 系统会自动抓取收藏视频并进行AI处理
5. 通过 SSE 实时推送同步进度

### 浏览知识库

1. **Dashboard（控制台）**：查看统计信息、分类看板、最近同步
2. **Library（知识库）**：浏览分类和标签，使用搜索功能
3. **Video Detail（视频详情）**：查看AI总结、关键要点、同类推荐

### 搜索功能

- **普通搜索**：基于SQLite的LIKE查询，支持标题和总结内容
- **语义搜索**：基于ChromaDB的向量检索，输入自然语言查询
  - 示例："找关于 Python 异步编程的内容"
  - 示例："如何提高专注力"
- **筛选器**：按分类/标签/质量分/收藏时间筛选

## API 文档

### API端点列表

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/health` | 健康检查 |
| `GET` | `/api/auth/status` | 检查登录状态 |
| `POST` | `/api/auth/check` | 详细检查登录状态 |
| `POST` | `/api/auth/clear` | 清除登录态 |
| `POST` | `/api/sync/start` | 启动同步任务 |
| `GET` | `/api/sync/status?task_id=xxx` | SSE 流，实时返回进度 |
| `POST` | `/api/sync/stop` | 中止同步 |
| `GET` | `/api/videos` | 分页获取视频列表 |
| `GET` | `/api/videos/:id` | 获取单个视频详情 |
| `PUT` | `/api/videos/:id` | 更新视频信息 |
| `DELETE` | `/api/videos/:id` | 删除视频 |
| `GET` | `/api/videos/categories` | 获取所有分类 |
| `GET` | `/api/videos/tags` | 获取所有标签 |
| `POST` | `/api/search` | 语义搜索 |
| `GET` | `/api/search/similar/:id` | 查找相似视频 |
| `GET` | `/api/stats` | 仪表盘统计 |
| `GET` | `/api/stats/config` | 获取配置状态 |
| `GET` | `/api/stats/health` | 后端健康检查 |

### Swagger UI

启动后端服务后，访问以下地址查看完整API文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 项目结构

```
dy_cliprepo/
├── backend/                          # Python 后端
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI 入口
│   │   ├── config.py                 # 配置管理
│   │   ├── database/
│   │   │   ├── models.py             # SQLAlchemy 模型
│   │   │   ├── sqlite_manager.py     # 数据库操作
│   │   │   └── chroma_manager.py     # 向量数据库
│   │   ├── scraper/
│   │   │   ├── auth.py               # 独立登录脚本
│   │   │   └── douyin_scraper.py     # 基于 auth.json 的只读同步
│   │   ├── ai/
│   │   │   ├── summarizer.py         # AI 总结与分类
│   │   │   ├── embedding.py          # 文本向量化
│   │   │   └── prompts.py            # Prompt 模板
│   │   ├── api/
│   │   │   ├── auth.py               # 认证路由
│   │   │   ├── sync.py               # 同步任务路由
│   │   │   ├── videos.py             # 视频相关路由
│   │   │   ├── search.py             # 搜索路由
│   │   │   └── stats.py              # 统计路由
│   │   └── services/
│   │       └── sync_service.py       # 同步任务编排
│   ├── data/                         # 数据目录
│   │   ├── auth.json                 # 登录态文件
│   │   ├── douyin_kb.db              # SQLite 数据库
│   │   ├── chromadb/                 # ChromaDB 数据
│   │   └── covers/                   # 封面图存储
│   ├── .env                          # 环境变量
│   ├── .env.example
│   ├── requirements.txt
│   └── venv/                         # Python 虚拟环境
│
├── frontend/                         # React 前端
│   ├── src/
│   │   ├── api/
│   │   │   └── client.ts             # API 封装
│   │   ├── components/               # 组件
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx         # 主控制台
│   │   │   ├── Library.tsx           # 知识库浏览
│   │   │   ├── VideoDetail.tsx       # 视频详情
│   │   │   └── Settings.tsx          # 设置
│   │   ├── types/
│   │   │   └── index.ts              # TypeScript 类型
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── docs/                             # 文档
├── start.bat                         # 启动脚本
├── login.bat                         # 登录脚本
└── README.md
```

## 数据库 Schema

### SQLite 表结构

```sql
CREATE TABLE videos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE NOT NULL,
    title TEXT,
    author TEXT,
    author_id TEXT,
    desc TEXT,
    cover_path TEXT,
    cover_url TEXT,
    summary TEXT,
    category TEXT,
    tags JSON,
    key_points JSON,
    quality_score INTEGER DEFAULT 0,
    created_at DATETIME,
    favorited_at DATETIME,
    synced_at DATETIME,
    updated_at DATETIME,
    embedding_id TEXT
);
```

### ChromaDB 集合

- **Collection**: `video_embeddings`
- **Documents**: `"{title}. {summary}. 标签：{tags}"`（用于语义匹配）
- **Metadatas**: `{"video_id": 123, "category": "编程技术", "url": "..."}`

## 常见问题

### Q: 登录态过期了怎么办？

A: 重新运行登录脚本：

```bash
login.bat
# 或
cd backend && python -m app.scraper.auth
```

### Q: Ollama 连接失败？

A: 确保 Ollama 服务已启动：

```bash
ollama serve
```

### Q: 同步过程中断了怎么办？

A: 支持断点续传，再次点击"同步收藏"即可，会自动跳过已同步的视频。

### Q: 如何切换 AI 模型？

A: 修改 `backend/.env` 文件中的 `AI_PROVIDER` 配置，然后重启后端。

### Q: 数据存储在哪里？

A: 所有数据存储在 `backend/data/` 目录：
- `auth.json` - 登录态
- `douyin_kb.db` - SQLite 数据库
- `chromadb/` - 向量数据库
- `covers/` - 封面图

## 许可证

本项目采用 [MIT 许可证](LICENSE) - 详见 LICENSE 文件

## 免责声明

- 本项目仅供个人学习使用，请勿用于商业用途
- 请遵守抖音的使用条款和相关法律法规
- 收藏内容可能涉及个人兴趣，请注意隐私保护
- 建议全程本地处理，避免将数据上传到第三方

## 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代、快速的Python Web框架
- [React](https://reactjs.org/) - 用于构建用户界面的JavaScript库
- [Playwright](https://playwright.dev/) - 现代化的浏览器自动化工具
- [ChromaDB](https://www.trychroma.com/) - 轻量级向量数据库
- [Ollama](https://ollama.ai/) - 本地大模型运行工具
- [Tailwind CSS](https://tailwindcss.com/) - 实用优先的CSS框架
