# Changelog

## [1.3.0] - 2026-06-28

### Fixed
- **AI 总结输出"页面不见啦"等错误文本** — `extract_video_page_info` 增加错误页检测：检查跳转 URL、过滤已知错误关键词、过滤导航/搜索 UI 文本
- **AI 总结截断/半句话** — `ai_service` 关闭 thinking 模式（输出走稳定的 `content` 字段），`max_tokens` 统一提升到 4096，`_extract_summary` 增加按 `【分类】` 分割的新策略
- **AI 总结重复标题和描述** — 系统提示词增加"禁止重复标题和描述"，模型输出不再经过不可控的 reasoning 提取

### Added
- **环形缓冲区日志系统** — `app/core/logger.py` 的 `RingBufferHandler` 保留最近 500 条日志，支持 `/api/debug/logs` 查询
- **DEBUG API** — `GET /api/debug/logs?n=100&level=INFO` 返回结构化日志（时间、级别、logger、消息），方便调试
- **AI 输入输出详细日志** — 每次 AI 调用记录 title、desc_len、video_url 状态、原始响应、提取结果，出现质量问题时可通过日志追溯

### Changed
- **详情页选择器优化** — `selectors.py` 新增优先选择器 `[class*="video-info"] [class*="desc"]`，新增 `VIDEO_PAGE_ERROR_KEYWORDS` 和 `VIDEO_PAGE_NOISE_KEYWORDS` 过滤
- **`extract_video_page_info` 重构** — 新增 `_is_noise_text()` 校验函数，登录/错误页 URL 检测
- **`main.py` lifespan** — 启动时调用 `setup_debug_logging()` 初始化日志系统

## [1.2.0] - 2026-06-28

### Added
- **GLM-4.6V-Flash 多模态模型** — 从纯文本 `glm-4.7-flash` 升级到支持视频理解的 `glm-4.6v-flash`
- **视频详情页抓取** — 同步时逐个打开视频详情页，提取完整简介和视频源地址（`sync_engine.extract_video_page_info`）
- **AI 双路由策略** — 描述 >= 50 字走 TEXT 模式，不足但有视频源走 VL 模式（`ai_service.generate_summary_and_category`）
- **增强同步流程** — `fetch_favorites_enriched` 复用浏览器会话，一次性完成列表抓取+详情页提取

### Changed
- **模型默认值** — `config.py` `ZHIPUAI_MODEL` 默认从 `glm-4.7-flash` 改为 `glm-4.6v-flash`
- **API 超时** — VL 模式 120s，TEXT 模式 30s（`ai_service.py`）
- **系统提示词** — 从"根据视频标题推测内容"改为"总结视频内容"，兼容两种模式
- **AGENTS.md** — 更新架构说明、同步流程、新增 AI 模型章节
- **selectors.py** — 新增 `VIDEO_DESC_DETAIL_SELECTORS` 和 `VIDEO_SOURCE_SELECTORS`

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
