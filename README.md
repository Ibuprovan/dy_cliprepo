# 抖音收藏 AI 知识库

> 让你的抖音收藏夹从吃灰的仓库，变成可沉淀、可检索的个人知识资产。

[![Python](https://img.shields.io/badge/python-3.11+-yellow.svg)](https://www.python.org/)
[![Node](https://img.shields.io/badge/node-18+-lightgreen.svg)](https://nodejs.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 关于这个项目

写这个工具的初衷很简单：我收藏了大量抖音视频，但收藏 ≠ 学会，时间久了根本找不到、想不起来。

我的设想是：**把抖音收藏夹当成一个"稍后看"的书签池"，定期把有价值的内容以 Markdown 的形式沉淀到自己的知识库（Obsidian、Notion、Logseq 等），真正把收藏变成自己的知识。**

然而，由于本人只是一名学生，**个人电脑算力不足以支撑 AI 模型实时分析视频内容**（无论是本地部署视觉语言模型还是云端视频理解 API，费用和延迟都是问题）。因此，当前的 AI 总结主要基于视频标题和文字描述，视频内容的深度理解尚未实现。

**这个项目目前处于"可用但不完善"的状态，作者暂无精力继续维护。** 如果你觉得有用，欢迎基于此项目继续开发；如果愿意分享改进，也非常欢迎提交 Pull Request。

---

## 功能说明

| 功能 | 说明 |
|------|------|
| **抖音收藏同步** | 通过 Playwright 自动登录，抓取全部收藏视频（含封面、作者、描述、收藏时间） |
| **AI 智能总结** | 基于视频标题和文字描述生成摘要，自动分类到知识维度（编程/商业/生活/心理学等） |
| **单条 Markdown 导出** | 在视频卡片上直接导出单条 Markdown，方便复制到知识库 |
| **分类浏览与筛选** | 按分类、时间、收藏状态筛选，支持批量删除 |
| **实时同步进度** | SSE 实时推送同步进度，随时了解抓取状态 |

### 当前局限性（诚实说明）

- AI 总结依赖视频的**文字描述**，无法理解视频画面内容（受限于本地算力和免费 API 的视频理解能力）
- 不支持**语义搜索**（embedding 需要额外部署向量数据库）
- 登录态约 7 天后需要重新扫码（抖音官方机制）

---

## 快速开始

### 环境要求

- **Python** 3.11+
- **Node.js** 18+
- **操作系统**：Windows 10/11（已针对 Windows 做了特殊适配）
- **网络**：能够访问抖音网页版和智谱 AI API

### 步骤一：克隆仓库

```bash
git clone https://github.com/Ibuprovan/dy_cliprepo.git
cd dy_cliprepo
```

### 步骤二：安装依赖

**后端（建议先创建虚拟环境）：**

```bash
cd backend

# 创建虚拟环境（Windows）
python -m venv venv
.\venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器（只需一次）
playwright install chromium
```

**前端：**

```bash
cd frontend
npm install
```

### 步骤三：配置环境变量

在后端目录创建 `.env` 文件（参考 `.env.example`）：

```env
# 智谱 AI API Key（免费额度：GLM-4.6V-Flash 每月 100 万 Token）
# 申请地址：https://open.bigmodel.cn/
ZHIPUAI_API_KEY=your_api_key_here
```

> **没有 API Key 怎么办？**
> AI 总结功能将退化为本地关键词提取模式（不调用 API，直接基于标题和描述生成摘要），工具仍可正常使用，但总结质量会下降。

### 步骤四：登录抖音

必须先完成一次扫码登录，后续同步才能读取收藏夹：

```bash
# 方式一：一键脚本（推荐双击运行）
login.bat

# 方式二：手动运行
cd backend
.\venv\Scripts\activate
python login_manual.py
```

运行后会弹出一个无头浏览器窗口，按照提示用抖音 App 扫码即可。登录成功后会保存登录态到 `backend/data/douyin_auth.json`，**约 7 天内无需重新登录**。

### 步骤五：启动服务

```bash
# 一键启动（推荐）
start.bat

# 或分别启动
# 终端 1：后端
cd backend
.\venv\Scripts\activate
python run_server.py

# 终端 2：前端
cd frontend
npm run dev
```

启动成功后，打开浏览器访问：

- **前端界面**：http://localhost:5173
- **后端 API 文档**：http://localhost:8000/docs

---

## 使用指南

### 同步收藏

1. 打开 http://localhost:5173
2. 在"同步收藏"输入框填入想抓取的数量（留空 = 全部），点击"开始同步"
3. 观察实时进度条和日志，了解抓取状态
4. 同步完成后，视频列表自动刷新

> **同步是增量更新**：已存在的视频（按 URL 去重）会被跳过，不会重复抓取。可以放心反复同步。

### 导出到知识库

每张视频卡片右上角有"下载 MD"按钮，点击即可导出单条 Markdown 文件，内容包含：

```markdown
# 视频标题

> AI 摘要内容

---

原视频链接：https://...
```

将导出的 Markdown 文件放入 Obsidian/Notion/Logseq 的仓库目录，即完成知识沉淀。

**建议流程**：每天/每周固定一个时间做一次"同步 + 导出"，形成规律的知识整理习惯。

### 浏览与筛选

- 点击顶部分类标签筛选对应类别的视频
- 鼠标悬停视频卡片展开 AI 摘要
- 选中多个视频后点击"批量删除"清理无效收藏

### 退出登录

如果需要换账号，点击右上角"退出登录"，再重新运行 `login.bat` 即可。

---

## 进阶用法

### 每日邮件推送（进阶需求，需自行扩展）

当前版本不包含自动邮件推送功能。以下是实现思路，供有能力的开发者参考：

```python
# 每日定时同步 + 导出 + 发送邮件伪代码
# 可使用 Windows 任务计划程序 / crontab 定时运行

import subprocess, smtplib, os
from email.mime.text import MIMEText
from datetime import datetime

# 1. 运行同步脚本
subprocess.run(["python", "test_sync.py"])

# 2. 读取今日新同步的视频（通过数据库查询 favorited_at）
new_videos = query_new_videos_since(last_run_time)

# 3. 生成 Markdown 摘要
email_body = "\n\n---\n\n".join([
    f"## {v.title}\n\n> {v.summary}\n\n[v.link]"
    for v in new_videos
])

# 4. 发送邮件（使用任意邮箱 SMTP）
msg = MIMEText(email_body, "plain")
msg["Subject"] = f"抖音收藏日报 {datetime.now().date()}"
# smtplib.SMTP("smtp.example.com", 587).send_message(msg)
```

### 配合 Obsidian / Notion 使用

1. 在 Obsidian/Notion 中创建一个固定文件夹/目录作为"抖音知识库"
2. 每次同步后，批量导出 Markdown 到该目录
3. 利用 Obsidian/Notion 的双链和标签功能做二次整理

### 定期自动同步（Windows 任务计划程序）

1. 打开"任务计划程序"（`taskschd.msc`）
2. 创建基本任务，设置触发器（如每天上午 9:00）
3. 操作选择"启动程序"，程序填 `python`，参数填 `run_server.py`（需写完整路径）
4. 配合 `curl` 或 Python 脚本定时调用 `POST /api/sync/start`

---

## 常见问题

### Q: 登录态过期了怎么办？

重新运行登录脚本即可：
```bash
login.bat
# 或
cd backend && python login_manual.py
```

### Q: 同步时浏览器崩溃或卡住？

1. 按 `Ctrl+C` 中止当前进程
2. 重启后端：`Stop-Process -Name python -Force; python run_server.py`
3. 重新点击"开始同步"（已抓取的视频会自动跳过）

### Q: 页面结构变化，视频抓不到或 AI 总结质量下降？

抖音网页版会不定期更新 DOM 结构。如果发现抓取失败：

1. 打开 `backend/app/scraper/selectors.py`，更新对应的 CSS 选择器
2. 查看 `backend/app/scraper/sync_engine.py` 中的选择器调用是否需要调整
3. 提交 PR 或 issue 帮助改进

### Q: API Key 如何获取？

1. 访问 [智谱 AI 开放平台](https://open.bigmodel.cn/)
2. 注册账号并完成实名认证
3. 在控制台创建 API Key
4. GLM-4.6V-Flash 有免费额度（每月 100 万 Token），普通用户足够

### Q: AI 总结质量很差，几乎是原文复制？

- 视频描述太短（抖音描述少于 50 字）：模型难以提取足够信息，可尝试手动编辑描述
- API 限流（429）：免费模型有频率限制，等待几分钟后重试
- API Key 未配置或配置错误：检查 `.env` 文件

### Q: 同步很慢，每次只能抓几十条？

抖音页面采用无限滚动加载机制，每次抓取后会滚动页面加载更多。如果网络较慢，可以适当减少每次同步的数量（如每次 50 条），分多次完成。

### Q: 能否抓取他人抖音账号的收藏？

**不能。** 工具读取的是浏览器登录态对应的账号收藏夹，无法访问他人账号。

### Q: 如何完全卸载？

1. 停止后端和前端进程
2. 删除项目目录
3. 删除 `backend/data/` 目录（包含数据库和登录态）
4. 删除 Python 虚拟环境目录 `backend/venv`

---

## 项目结构

```
dy_cliprepo/
├── backend/                          # Python FastAPI 后端
│   ├── app/
│   │   ├── main.py                   # FastAPI 入口、CORS、lifespan
│   │   ├── core/
│   │   │   ├── config.py             # 所有配置（路径、API Key、浏览器参数）
│   │   │   └── logger.py             # 环形缓冲区日志系统
│   │   ├── api/v1/
│   │   │   ├── videos.py             # 视频 CRUD、批量删除
│   │   │   ├── sync.py               # 同步任务启动、停止、SSE 进度
│   │   │   ├── auth.py               # 登录态检查与退出
│   │   │   └── debug.py              # 调试日志查询
│   │   ├── services/
│   │   │   ├── sync_service.py       # 同步任务编排（独立线程）
│   │   │   └── ai_service.py         # AI 总结与分类（智谱 GLM-4.6V-Flash）
│   │   ├── repositories/
│   │   │   ├── video_repo.py         # 视频数据 CRUD（参数化查询防注入）
│   │   │   └── task_repo.py          # 同步任务状态管理
│   │   ├── db/
│   │   │   └── database.py           # aiosqlite 单例（SQLite WAL 模式）
│   │   ├── scraper/
│   │   │   ├── sync_engine.py        # Playwright 无头抓取
│   │   │   ├── auth_manager.py       # 登录态管理
│   │   │   └── selectors.py          # 抖音页面 CSS 选择器
│   │   └── models/
│   │       └── video.py              # Pydantic 数据模型
│   ├── data/                         # 本地数据（gitignored）
│   │   ├── app.db                   # SQLite 数据库
│   │   └── douyin_auth.json         # Playwright 登录态（cookies + localStorage）
│   ├── run_server.py                # Windows 启动脚本（设置事件循环策略）
│   ├── login_manual.py               # 独立登录脚本
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/                         # React + TypeScript + Tailwind v4 前端
│   ├── src/
│   │   ├── App.tsx                  # 主页面、状态管理
│   │   ├── api/client.ts            # fetch 封装
│   │   ├── components/
│   │   │   ├── VideoTable.tsx        # 视频卡片列表、分类筛选、批量操作
│   │   │   ├── SyncPanel.tsx        # 同步控制面板
│   │   │   └── Layout.tsx           # 页面布局
│   │   ├── hooks/
│   │   │   └── useSync.ts           # SSE 连接管理
│   │   └── types/index.ts           # TypeScript 类型定义
│   └── package.json
│
├── docs/                             # 文档（可选扩展）
├── start.bat                         # 一键启动前后端
├── login.bat                         # 登录脚本
├── AGENTS.md                         # 开发者维护文档
├── CHANGELOG.md                      # 版本更新记录
├── CODE_WIKI.md                      # 项目架构详细说明
└── README.md
```

---

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **前端** | React 19 + TypeScript | 组件化 UI，TypeScript 类型保障 |
| **样式** | Tailwind CSS v4 | 原子化 CSS，通过 Vite 插件集成 |
| **后端** | Python FastAPI | 异步高性能框架，天然支持 SSE |
| **数据库** | SQLite（aiosqlite） | WAL 模式，零配置本地存储 |
| **浏览器自动化** | Playwright | 比 Selenium 更现代，支持保存登录态 |
| **AI** | 智谱 GLM-4.6V-Flash | 免费多模态模型（文字理解），视频内容理解受算力限制 |
| **日志** | RingBufferHandler | 内存环形缓冲区，保留最近 500 条，支持查询 |

---

## 免责声明

- 本项目仅供个人学习与研究使用，请勿用于商业用途或大规模爬取
- 请遵守抖音的使用条款和相关法律法规
- 收藏内容可能涉及个人隐私，请妥善保管本地数据
- 作者不对因使用本工具造成的任何后果承担责任

---

## 贡献与联系

当前项目维护状态：**低优先级维护**

如果你有意继续开发，欢迎提交 Pull Request。以下是一些可能的改进方向：

- [ ] 集成本地视觉语言模型（如 Qwen2.5-VL、LLava）进行视频内容理解
- [ ] 添加 embedding 向量搜索（ChromaDB / Qdrant）
- [ ] 实现每日邮件定时推送
- [ ] 支持更多平台（微博、B站、小红书）
- [ ] 添加视频封面图缓存与展示优化
- [ ] 国际化（多语言支持）

如有问题或建议，欢迎在 GitHub 提 Issue。

---

*希望这个工具能帮你把收藏夹里的"知识"真正变成自己的知识。*
