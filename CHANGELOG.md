# Changelog

## [1.1.0] - 2026-06-28

### Fixed
- **[Critical] SQL 注入漏洞** — `video_repo.py` 和 `task_repo.py` 的 `update` 函数列名未校验，添加 `ALLOWED_COLUMNS` 白名单
- **[Critical] 路径穿越漏洞** — `main.py` SPA catch-all 路由可读取服务器任意文件，添加 `resolve()` + 前缀校验
- **[Critical] NotImplementedError** — Playwright 在 uvicorn 中无法启动浏览器，改用 `threading` 独立线程方案
- **SPA catch-all 吞掉 API 404** — `/api/` 和 `/health` 路径不再走 SPA fallback
- **JSON 解析无容错** — `video_repo.py` 的 `_row_to_video` 添加 `_safe_json_loads` 防止脏数据崩溃
- **SSE 断连静默关闭** — `client.ts` 增加 `onError` 回调，`useSync.ts` 显示断连提示
- **cancelled 状态映射错误** — `useSync.ts` 使用 `statusMap` 正确映射 `cancelled` 状态
- **SSE 超时太短** — 从 5 分钟改为 30 分钟
- **CSS reset 与 Tailwind 冲突** — 删除手动 reset，依赖 Tailwind Preflight
- **热重载丢失事件循环策略** — `main.py` 中也设置 `WindowsProactorEventLoopPolicy`
- **数据库连接无健康检查** — `database.py` 的 `get_db` 添加 `SELECT 1` 检查 + 自动重连
- **异步函数中同步 I/O** — `sync_service.py` 改用 `asyncio.to_thread`
- **类型注解不正确** — `sync.py` 的 `stop_sync` 改为 `Optional[str]`
- **依赖安装失败继续执行** — `start.bat` 改为失败时中止

### Changed
- **启动脚本全英文输出** — `start.bat` 改为英文，避免编码问题导致闪退
- **启动脚本登录引导** — `start.bat` 检测到无登录态时自动提示登录
- **前端启动命令提示** — `App.tsx` 改为 `python run_server.py`
- **AGENTS.md 中文重写** — 全面更新项目文档

### Added
- `start_login.bat` — 独立登录脚本，双击即可扫码登录
- `docs/tasks/TASK-001.md` — 全项目 Bug 排查记录

## [1.0.0] - 2026-06-24

### Added
- FastAPI 后端 + React/Vite 前端
- Playwright 抖音收藏抓取
- SQLite 数据库存储
- SSE 实时同步进度
- Tailwind CSS v4 前端样式
