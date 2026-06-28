# AGENTS.md

## 项目概述

抖音收藏 AI 知识库 — 本地工具，通过 Playwright 抓取抖音收藏视频，AI 总结，语义搜索。Windows 优先。

前后端分离：Python FastAPI 后端 (端口 8000) + React/Vite 前端 (端口 5173)。

## 关键：Windows asyncio + Playwright 兼容性

Playwright 需要 `ProactorEventLoop` 才能创建子进程启动浏览器。在 Windows 上：

- **必须通过 `run_server.py` 启动后端**，不能直接用 `uvicorn`。该脚本在 uvicorn 加载前设置了 `WindowsProactorEventLoopPolicy`。
- **绝对不能用裸 `uvicorn app.main:app`** — 某些 Python 版本默认使用 `SelectorEventLoop`，会静默失败，无法启动浏览器。
- **同步任务在独立线程中运行** — `sync_service.py` 使用 `threading.Thread` + `asyncio.new_event_loop()`，避免 uvicorn 事件循环与 Playwright 子进程冲突。

```bash
cd backend && python run_server.py    # 正确
cd backend && uvicorn app.main:app    # 错误 — 同步会卡死
```

## 快速启动

```bash
start.bat                # 完整启动（自动创建 venv、安装依赖、启动前后端）
login.bat                # 首次抖音登录（同步前必须先登录）
```

## 开发命令

### 后端
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium     # 首次需下载浏览器
python run_server.py            # 端口 8000
python login_manual.py          # 独立登录脚本
python test_sync.py             # 手动同步测试（拉取 1 条）
python diagnose.py              # 环境诊断
```

依赖：fastapi, uvicorn, playwright, pydantic, aiosqlite。

### 前端
```bash
cd frontend
npm install
npm run dev        # Vite 开发服务器 (端口 5173)
npm run build      # tsc + vite 构建
npm run lint       # eslint
```

## 架构

```
backend/app/
  main.py              # FastAPI 入口，lifespan，CORS
  core/config.py       # 所有路径基于 BASE_DIR 派生，禁止硬编码
  api/v1/              # 路由处理（health, sync, videos）
  services/            # 业务逻辑（sync_service, video_service）
  repositories/        # 数据库访问（video_repo, task_repo）
  db/database.py       # aiosqlite 单例，建表逻辑
  scraper/
    auth_manager.py    # 登录流程，storage_state 加载/验证
    sync_engine.py     # Playwright 无头抓取，setup_sync_logger()
    selectors.py       # 抖音页面 CSS 选择器（页面结构变化时改这里）
  models/video.py      # Video 数据类
```

启动链路：`main.py` lifespan → `ensure_dirs()` → `setup_sync_logger()` → `init_db()`。

同步流程：API `/api/sync/start` → `sync_service.start_sync()` → `threading.Thread` → `_run_sync_task` → `sync_engine.fetch_favorites_enriched()` → Playwright 无头模式 → 收藏列表 + 逐个打开视频详情页提取完整描述和视频源 → AI 双路由（text 模式或 VL 模式）→ 存入 SQLite。

## 数据存储

SQLite 数据库：`backend/data/app.db`（WAL 模式，启用外键）。登录态：`backend/data/douyin_auth.json`（Playwright `storage_state`，包含 cookies + localStorage，**不是只存 cookies**）。

所有路径来自 `app/core/config.py`，禁止硬编码路径。

## 抖音抓取注意事项

- **反检测**：`BROWSER_ARGS`、`USER_AGENT`、`STEALTH_JS` 在 config.py 中。禁用 webdriver 指纹。如果抖音更新检测机制，改这里。
- **选择器**：所有 CSS 选择器在 `scraper/selectors.py`。抓取失败（标题为空、找不到视频）时首先检查此文件 — 抖音页面结构经常变化。
- **登录过期**：Cookie 约 7 天失效。同步报认证错误时重新运行 `login_manual.py`。
- **storage_state，不是 cookies**：代码保存 `context.storage_state()`，包含 cookies + localStorage。抖音的部分登录态存在 localStorage 中。

## 前端

单页 React 应用（`frontend/src/App.tsx`），使用 Tailwind CSS v4 + Vite 代理。不用 axios，用原生 `fetch`。`/api` 和 `/health` 请求在开发时代理到 `localhost:8000`。

## AI 模型

- **默认模型**：`glm-4.6v-flash`（智谱免费多模态模型，支持文本+视频理解）
- **双路由策略**：视频详情页描述 >= 50 字 → TEXT 模式（上传描述文本）；描述不足但有视频源 → VL 模式（上传视频 URL 分析）
- **推理模型输出**：`content` 字段为空，输出在 `reasoning_content`。`ai_service.py` 的 `_extract_summary()` 从推理文本中提取最终总结段落
- **限流处理**：免费模型有频率限制（429），`generate_summary_and_category` 内部自动退化到描述截取 fallback
- **旧模型**：之前使用 `glm-4.7-flash`，现已统一迁移到 `glm-4.6v-flash`

## 注意事项

- **没有自动化测试**：`backend/test_*.py` 是手动诊断脚本，不是 pytest 测试套件。没有 CI/CD。
- **数据目录被 gitignore**：`backend/data/` 内容不在仓库中。首次运行通过 `ensure_dirs()` 自动创建目录。
- **Playwright 浏览器**：venv 创建后必须运行 `playwright install chromium`。浏览器二进制文件不在仓库中。
- **README 过时**：描述了尚未实现的功能。以代码为准。
- **前端使用 Tailwind v4**：用的是 `@tailwindcss/vite` 插件，不是 PostCSS 配置。样式用 Tailwind 工具类写在 JSX 中。
