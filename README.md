# 抖音收藏 AI 知识库 (Douyin Knowledge Base)

> 让你的抖音收藏夹从吃灰的仓库，变成可检索、可分类、可复用的个人知识资产。

![版本徽章](https://img.shields.io/badge/version-1.0.0-blue.svg)
![许可证徽章](https://img.shields.io/badge/license-MIT-green.svg)
![Python版本](https://img.shields.io/badge/python-3.11+-yellow.svg)
![Node版本](https://img.shields.io/badge/node-18+-lightgreen.svg)

## 📖 项目简介

这是一个专为重度抖音用户设计的本地私有化知识管理工具。它通过浏览器自动化技术抓取你的抖音收藏视频，利用 AI 对视频内容进行智能总结、自动分类和标签提取，最终构建成一个支持语义搜索的结构化知识库。

所有数据存储在本地，无需担心隐私泄露，也无需依赖抖音官方 API。

**核心理念：「收藏不等于拥有，检索才能创造价值。」**

我们不追求替代抖音的娱乐体验，而是解决「收藏后遗忘」的信息管理痛点。通过 AI 将非结构化的短视频内容转化为结构化的知识节点，让你的每一次收藏都真正沉淀为认知资产。

## ✨ 功能特性

| 能力 | 说明 |
|------|------|
| 🔄 一键同步 | 自动登录抖音网页版，抓取收藏列表，支持断点续传和增量更新 |
| 🤖 AI 智能总结 | 基于大语言模型（支持本地 Ollama / 云端 API）自动生成视频核心要点、干货评分 |
| 📁 自动分类体系 | 将杂乱的收藏自动归类到「编程技术 / 商业思维 / 生活技巧 / 心理学」等知识维度 |
| 🔍 语义搜索引擎 | 不是简单的关键词匹配——输入"如何提高专注力"，能搜到相关的心理学和学习方法视频 |
| 🔒 私有化部署 | 前后端完全本地运行，视频数据、AI 处理、向量数据库均不出境 |
| 📊 现代化看板 | React 驱动的可视化界面，支持分类浏览、时间轴、标签云和质量筛选 |

## 🏗️ 技术架构

### 架构图

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

### 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **前端** | React 18 + TypeScript + Tailwind CSS + Shadcn/ui | 现代化UI框架，响应式设计 |
| **后端** | Python FastAPI | 异步高性能，天然支持 SSE（实时推送同步进度） |
| **数据库** | SQLite + ChromaDB | 结构化存储 + 向量检索，零配置本地部署 |
| **AI层** | Ollama / OpenAI / DeepSeek | 支持本地模型（推荐 Qwen2.5）或云端 API |
| **自动化** | Playwright | 比 Selenium 更现代，能穿透抖音的反爬，且支持保存登录态 |

### 数据流

```
Playwright 抓取 → AI 总结与向量化 → SQLite 结构化存储 + ChromaDB 语义索引 → React 可视化消费
```

## 📸 截图

### Dashboard 控制台
![Dashboard截图占位](./docs/screenshots/dashboard.png)

**功能说明：**
- 顶部统计卡片：总收藏数 | 本月新增 | 分类数 | 平均质量分
- 分类看板：网格展示各分类下的视频数量（点击穿透到列表）
- 最近同步：时间轴展示最近处理的 10 条视频

### Library 知识库
![Library截图占位](./docs/screenshots/library.png)

**功能说明：**
- 左侧边栏：分类树 + 标签云
- 中间内容区：视频卡片网格（封面 + AI 总结 + 分类标签）
- 搜索栏：支持普通关键词搜索和语义搜索

### Video Detail 视频详情
![VideoDetail截图占位](./docs/screenshots/video-detail.png)

**功能说明：**
- 左侧：嵌入抖音网页播放器（或跳转链接）
- 右侧：AI 总结卡片 + 关键要点列表 + 原始描述
- 底部：同类推荐（基于向量相似度）

### Settings 设置
![Settings截图占位](./docs/screenshots/settings.png)

**功能说明：**
- AI 模型配置：Ollama 模型名 / OpenAI API Key
- 同步设置：每次同步数量限制、是否下载封面
- 数据管理：导出 JSON / 清空库

## 🚀 安装指南

### 环境要求

- **Python**: 3.11 或更高版本
- **Node.js**: 18 或更高版本
- **Git**: 用于克隆仓库
- **操作系统**: Windows 10/11（推荐）

### 后端安装

```bash
# 1. 克隆仓库
git clone https://github.com/Ibuprovan/dy_cliprepo.git
cd dy_cliprepo

# 2. 创建Python虚拟环境
cd backend
python -m venv venv
.\venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 安装Playwright浏览器
playwright install chromium
```

### 前端安装

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖
npm install

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置后端API地址
```

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

```bash
# 在 backend/app/config.py 中配置
OPENAI_API_KEY=your-api-key
DEEPSEEK_API_KEY=your-api-key
```

### 启动服务

```bash
# 终端 1：启动 Ollama（如果走本地模型）
ollama run qwen2.5:14b

# 终端 2：启动后端
cd backend
.\venv\Scripts\activate
uvicorn app.main:app --reload --port 8000

# 终端 3：启动前端
cd frontend
npm run dev
```

访问 http://localhost:5173 打开前端界面

## 📚 使用说明

### 首次登录

1. 启动后端和前端服务
2. 打开前端界面 http://localhost:5173
3. 点击"登录抖音"按钮
4. 在弹出的浏览器窗口中使用抖音APP扫码登录
5. 登录成功后，Cookie 会自动保存到本地

### 同步收藏

1. 登录后点击"同步收藏"按钮
2. 系统会自动打开抖音网页版，进入个人主页的收藏Tab
3. 自动滚动加载所有收藏视频
4. 对每个新视频进行AI总结、分类和标签提取
5. 通过 SSE 实时推送同步进度到前端
6. 支持断点续传，可随时中止和恢复

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

## 🔌 API 文档

### API端点列表

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/sync/start` | 启动同步任务，返回 `task_id` |
| `GET` | `/api/sync/status?task_id=xxx` | SSE 流，实时返回进度 |
| `POST` | `/api/sync/stop` | 中止同步 |
| `GET` | `/api/videos` | 分页获取视频列表（支持 category/tag 筛选） |
| `GET` | `/api/videos/:id` | 获取单个视频详情 |
| `POST` | `/api/search` | 语义搜索（查询向量化后在 Chroma 检索） |
| `GET` | `/api/stats` | 仪表盘统计（总数、分类分布、收藏趋势） |
| `POST` | `/api/ai/regenerate` | 对单个视频重新 AI 总结（调参后重跑） |

### Swagger UI

启动后端服务后，访问以下地址查看完整API文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 请求示例

```bash
# 启动同步任务
curl -X POST http://localhost:8000/api/sync/start

# 查询同步状态（SSE）
curl -N http://localhost:8000/api/sync/status?task_id=xxx

# 获取视频列表（分页）
curl http://localhost:8000/api/videos?page=1&size=20&category=编程技术

# 语义搜索
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Python异步编程", "limit": 10}'

# 获取统计数据
curl http://localhost:8000/api/stats
```

### SSE 进度推送示例

```javascript
// 前端监听同步进度
const eventSource = new EventSource('/api/sync/status?task_id=xxx');

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(`进度: ${data.progress}%`);
  console.log(`当前处理: ${data.current_title}`);
};
```

## 📁 项目结构

```
dy_cliprepo/
├── backend/                          # Python 后端
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI 入口
│   │   ├── config.py                 # 配置管理（模型选择、API Key）
│   │   ├── database/
│   │   │   ├── models.py             # SQLAlchemy 模型
│   │   │   ├── sqlite_manager.py     # 数据库操作
│   │   │   └── chroma_manager.py     # 向量数据库
│   │   ├── scraper/
│   │   │   ├── douyin_scraper.py     # Playwright 抓取核心
│   │   │   └── auth_manager.py       # Cookie/登录态管理
│   │   ├── ai/
│   │   │   ├── summarizer.py         # AI 总结与分类
│   │   │   ├── embedding.py          # 文本向量化
│   │   │   └── prompts.py            # 所有 Prompt 模板
│   │   ├── api/
│   │   │   ├── videos.py             # 视频相关路由
│   │   │   ├── sync.py               # 同步任务路由
│   │   │   └── search.py             # 搜索路由
│   │   └── services/
│   │       └── sync_service.py       # 同步任务编排（核心逻辑）
│   ├── requirements.txt
│   └── alembic/                      # 数据库迁移
│
├── frontend/                         # React 前端
│   ├── src/
│   │   ├── components/
│   │   │   ├── VideoCard.tsx         # 视频卡片
│   │   │   ├── CategoryBoard.tsx     # 分类看板
│   │   │   ├── SyncProgress.tsx      # 同步进度条
│   │   │   └── SearchBar.tsx         # 语义搜索框
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx         # 主控制台
│   │   │   ├── Library.tsx           # 知识库浏览
│   │   │   └── Settings.tsx          # 设置（AI模型配置）
│   │   ├── hooks/
│   │   │   ├── useSync.ts            # 同步任务 Hook
│   │   │   └── useSearch.ts          # 搜索 Hook
│   │   ├── api/
│   │   │   └── client.ts             # axios 封装
│   │   └── types/
│   │       └── index.ts              # TypeScript 类型定义
│   ├── package.json
│   └── tailwind.config.js
│
├── docs/                             # 文档
│   ├── screenshots/                  # 截图
│   │   ├── dashboard.png
│   │   ├── library.png
│   │   ├── video-detail.png
│   │   └── settings.png
│   └── api.md                        # API文档
│
└── README.md
```

## 🛠️ 开发指南

### 开发环境设置

```bash
# 后端开发（热重载）
cd backend
.\venv\Scripts\activate
uvicorn app.main:app --reload --port 8000

# 前端开发（热重载）
cd frontend
npm run dev
```

### 代码规范

- **Python**: PEP 8, Black 格式化
- **TypeScript**: ESLint + Prettier
- **提交信息**: Conventional Commits 格式

```bash
# 提交信息格式
feat: 添加新功能
fix: 修复bug
docs: 更新文档
style: 代码格式调整
refactor: 重构代码
test: 添加测试
chore: 构建/工具变动
```

### 数据库 Schema

#### SQLite 表结构

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

#### ChromaDB 集合

- **Collection**: `video_embeddings`
- **Documents**: `"{title}. {summary}. 标签：{tags}"`（用于语义匹配）
- **Metadatas**: `{"video_id": 123, "category": "编程技术", "url": "..."}`

## 🚢 部署指南

### Windows 本地部署

```bash
# 1. 按照安装指南配置环境

# 2. 启动后端（生产模式）
cd backend
.\venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 3. 构建并启动前端
cd frontend
npm run build
npm run preview
```

### 开机自启动（可选）

创建 Windows 任务计划程序，添加启动脚本：

```batch
@echo off
cd /d C:\path\to\dy_cliprepo\backend
call venv\Scripts\activate
start /B uvicorn app.main:app --host 0.0.0.0 --port 8000

cd /d C:\path\to\dy_cliprepo\frontend
start /B npm run preview
```

## 🤝 贡献指南

### 如何贡献

1. **Fork** 本仓库
2. **创建特性分支**: `git checkout -b feature/your-feature`
3. **提交更改**: `git commit -m 'feat: 添加某功能'`
4. **推送分支**: `git push origin feature/your-feature`
5. **提交 Pull Request**

### Issue 模板

- **Bug 报告**: 描述问题、复现步骤、期望行为、实际行为
- **功能请求**: 描述需求、使用场景、期望效果
- **问题咨询**: 描述问题、已尝试的解决方案

### Pull Request 模板

- **变更描述**: 说明本次PR的内容
- **相关Issue**: 关联的Issue编号
- **测试情况**: 是否已测试，测试环境
- **截图**: 如有UI变更，请提供截图

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE) - 详见 LICENSE 文件

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代、快速的Python Web框架
- [React](https://reactjs.org/) - 用于构建用户界面的JavaScript库
- [Playwright](https://playwright.dev/) - 现代化的浏览器自动化工具
- [ChromaDB](https://www.trychroma.com/) - 轻量级向量数据库
- [Ollama](https://ollama.ai/) - 本地大模型运行工具
- [Tailwind CSS](https://tailwindcss.com/) - 实用优先的CSS框架
- [Shadcn/ui](https://ui.shadcn.com/) - 现代化UI组件库

## 📞 联系方式

- **GitHub**: [@Ibuprovan](https://github.com/Ibuprovan)
- **项目链接**: [https://github.com/Ibuprovan/dy_cliprepo](https://github.com/Ibuprovan/dy_cliprepo)

## ⚠️ 免责声明

- 本项目仅供个人学习使用，请勿用于商业用途
- 请遵守抖音的使用条款和相关法律法规
- 收藏内容可能涉及个人兴趣，请注意隐私保护
- 建议全程本地处理，避免将数据上传到第三方

## 🔮 未来规划

- [ ] 支持更多平台（B站、小红书等）
- [ ] 添加视频内容转录功能
- [ ] 支持知识图谱可视化
- [ ] 添加移动端适配
- [ ] 支持多用户协作
- [ ] 添加数据导出功能（Markdown、JSON、CSV）
