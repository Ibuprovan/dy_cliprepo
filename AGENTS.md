# AGENTS.md

## 项目概述

抖音收藏 AI 知识库 — 本地工具，通过 Playwright 抓取抖音收藏视频，AI 总结，语义搜索。Windows 优先。

前后端分离：Python FastAPI 后端 (端口 8000) + React/Vite 前端 (端口 5173)。

## 关键：Windows asyncio + Playwright 兼容性

Playwright 需要 `ProactorEventLoop` 才能创建子进程启动浏览器。在 Windows 上：

- **必须通过 `run_server.py` 启动后端**，不能直接用 `uvicorn`。该脚本在 uvicorn 加载前设置了 `WindowsProactorEventLoopPolicy`。
- **绝对不能用裸 `uvicorn app.main:app`** — 某些 Python 版本默认使用 `SelectorEventLoop`，会静默失败，无法启动浏览器。
- **同步任务在独立线程中运行** — `sync_service.py` 使用 `threading.Thread` + `asyncio.new_event_loop()`，避免 uvicorn 事件循环与 Playwright 子进程冲突。
- **热重载可能崩**：WatchFiles reload 有时会杀死子进程导致后端不响应。此时手动 `Stop-Process -Name python -Force` 后重启。

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

依赖：fastapi, uvicorn, playwright, pydantic, aiosqlite, httpx, python-dotenv。

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
  core/
    config.py          # 所有路径基于 BASE_DIR 派生，禁止硬编码
    logger.py          # RingBufferHandler 调试日志系统（保留 500 条）
  api/v1/
    __init__.py        # 聚合所有路由
    health.py          # GET /health
    videos.py          # CRUD + POST /api/videos/delete-batch
    sync.py            # POST /api/sync/start, SSE /api/sync/status/{id}
    auth.py            # POST /api/auth/logout, GET /api/auth/status
    debug.py           # GET /api/debug/logs?n=100&level=INFO
  services/
    sync_service.py    # 同步业务流程（threading.Thread 独立线程）
    ai_service.py      # GLM-4.6V-Flash 双路由（TEXT / VL），fallback
  repositories/
    video_repo.py      # 视频 CRUD，列名白名单防 SQL 注入
    task_repo.py       # 同步任务状态管理
  db/database.py       # aiosqlite 单例，WAL 模式
  scraper/
    auth_manager.py    # 登录流程，storage_state 加载/验证
    sync_engine.py     # Playwright 无头抓取 + 详情页提取
    selectors.py       # 抖音页面 CSS 选择器（更新日志写在这里）
  models/video.py      # VideoCreate、VideoDB、VideoResponse 数据类
```

启动链路：`main.py` lifespan → `ensure_dirs()` → `setup_debug_logging()` → `setup_sync_logger()` → `init_db()`。

## 同步流程

```
POST /api/sync/start
  → sync_service.start_sync()
    → threading.Thread → _run_sync_task
      → sync_engine.fetch_favorites_enriched(limit)
        → Playwright 无头浏览器 → 收藏列表滚动
        → 对每个新视频:
            a. 打开视频详情页获取完整 desc + video_src_url
            b. _is_noise_text() 过滤播放器 UI 文本
            c. 返回 enriched 视频列表
      → 对每个新视频:
            generate_summary_and_category(title, desc, video_url)
              → desc干净 → TEXT模式（GLM-4.6V-Flash）
              → desc短+video_url → VL模式（分析视频 URL）
              → 都无 → title fallback
            → 摘要 + 分类写入 SQLite
```

## 数据存储

SQLite 数据库：`backend/data/app.db`（WAL 模式，启用外键）。
登录态：`backend/data/douyin_auth.json`（Playwright `storage_state`，包含 cookies + localStorage，**不是只存 cookies**）。
所有路径来自 `app/core/config.py`，禁止硬编码路径。

## AI 模型

- **默认模型**：`glm-4.6v-flash`（智谱免费多模态模型，支持文本+视频理解）
- **thinking 已关闭**：`thinking: {"type": "disabled"}`，输出走 `content` 字段（稳定可控），`reasoning_content` 做兜底
- **双路由**：描述 >= 50 字 → TEXT 模式；不足但有视频源 → VL 模式
- **max_tokens**：统一 4096
- **限流处理**：免费模型频率限制（429），自动退化到描述截取 fallback
- **摘要提取**：_extract_summary 按 `【分类：xxx】` 分割取最前，兜底到引号/段落/句子

## 调试日志系统

```
GET /api/debug/logs?n=100&level=INFO
{
  "logs": [
    {"time": "2026-06-28T14:30:00", "level": "INFO", "logger": "...", "message": "..."}
  ],
  "count": 2
}
```
- RingBufferHandler 保留最近 500 条日志
- 每次 AI 调用自动记录：title、desc_len、video_url 状态、原始响应、提取结果
- 出现质量问题时通过日志回溯

## 已知问题与注意事项

1. **播放器 UI 文本过滤** — `_is_noise_text()` 检测 `XX:XX / XX:XX` 时间格式和「倍速/清屏/连播/章节要点」关键词。如果抖音页面结构变化，改 `selectors.py` 中的 `VIDEO_PAGE_NOISE_KEYWORDS`
2. **详情页描述难抓** — 抖音详情页 DOM 使用 hash class，没有稳定选择器。多次迭代调整，目前依赖 `desc` 相关 class 前缀
3. **选择器优先顺序**：先特定（video-info desc）→ 再通用（span/div/p 含 desc），避免匹配播放器叠加层
4. **post-stop 后端被杀** — `Stop-Process -Name python -Force` 会杀掉所有 Python 进程，包括后端。之后需要 `Start-Process` 重启
5. **没有自动化测试** — `backend/test_*.py` 是手动诊断脚本，不是 pytest 测试套件。没有 CI/CD。
6. **登录过期** — Cookie 约 7 天失效，报认证错误时重新运行 `login_manual.py`
7. **README 过时** — 描述了尚未实现的功能。以代码为准。
8. **前端使用 Tailwind v4** — 用 `@tailwindcss/vite` 插件，不是 PostCSS 配置。样式用 Tailwind 工具类写在 JSX 中。
9. **数据目录被 gitignore** — `backend/data/` 不在仓库中。首次运行通过 `ensure_dirs()` 自动创建
10. **Playwright 浏览器二进制** — 不在仓库中，venv 创建后必须运行 `playwright install chromium`
11. **后端绑定 127.0.0.1** — 本地工具只监听回环接口，不对外暴露。AGENTS.md 早期版本的 `0.0.0.0` 已修正。
12. **GLM 限流** — 免费模型 `glm-4.6v-flash` 触发 429 时自动重试 3 次（间隔 2/4/6 秒）。完全失败走本地兜底（智能提取 + 关键词分类）。

## API 路由表

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /health | 健康检查 |
| GET | /api/videos | 视频列表（?limit=&offset=&category=） |
| GET | /api/videos/categories | 分类列表 |
| GET | /api/videos/{id} | 单个视频 |
| PUT | /api/videos/{id} | 更新视频 |
| DELETE | /api/videos/{id} | 删除单个视频 |
| POST | /api/videos/delete-batch | 批量删除（body: {ids: [...]}） |
| POST | /api/sync/start | 启动同步（?limit=） |
| POST | /api/sync/stop | 停止同步 |
| GET | /api/sync/status/{task_id} | SSE 同步进度 |
| POST | /api/auth/logout | 退出登录（删除 storage_state） |
| GET | /api/auth/status | 登录态检查 |
| GET | /api/debug/logs | 调试日志 |

## 最近提交历史

```
feat: 重写 AI 摘要：429 重试 + 智能 fallback + 本地分类
fix: 修复同步后点击"全部"分类无法加载视频
fix: 15 项 bug 与安全修复（后端安全/任务状态/SSE + 前端状态管理/UI）
docs: 添加 UPDATE.md 更新日志 + AGENTS.md 同步
f1e30c4 fix: 过滤播放器UI文本防止AI总结倍速/清屏/连播/时间戳等垃圾内容
4cf6468 fix: AI总结质量修复 + 调试日志系统
f3a0689 feat: 多选视频批量删除 + 一键全选
0b9b19c feat: 升级 GLM-4.6V-Flash 多模态模型 + 视频详情页抓取 + AI 双路由
41895c8 fix: 5 issues - cover, title, summary, delete, category
888c6ed feat: add sync-all, AI categorization, card layout, Markdown download, logout
75efb1f feat: AI 摘要升级 100-200 字完整总结
4443b1c feat: 集成 GLM-4.7-Flash AI 摘要
fcbdc7b fix: 修复安全漏洞、同步崩溃、启动脚本闪退
c791cb4 refactor: 架构优化 - 分层架构、SQLite、组件化前端
```

> 完整更新内容见 [UPDATE.md](UPDATE.md)

## 未来方向

- **VL 视频理解强化**：当前 VL 模式用 GLM-4.6V-Flash 分析视频 URL，效果取决于模型能否访问 Douyin CDN
- **本地 VL 模型**：用户有 RTX 4060 (4GB)，可考虑 Ollama + Qwen3-VL-2B q4 量化
- **语义搜索**：当前缺乏 embedding 和搜索
- **统计面板**：分类分布图、同步历史等
