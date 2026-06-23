# 更新日志

本项目所有重要更改都将记录在此文件。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)。

---

## [1.1.0] - 2026-06-23

### 架构优化

全面重构项目架构，提升代码质量、可维护性和稳定性。

#### 后端

**新增**
- SQLite 数据库支持（替代 JSON 文件存储）
- 分层架构：API → Service → Repository → DB
- 路由版本管理（`/api/v1/`）
- 任务状态持久化（服务重启不丢失）
- CSS 选择器集中管理（`selectors.py`）
- Pydantic 数据模型（`models/video.py`）
- pytest 测试框架（3 个 smoke test）
- 数据迁移脚本（`scripts/migrate_json_to_sqlite.py`）
- `/api/sync/stop` 端点（支持取消同步）

**修复**
- 线程安全：添加 `threading.Lock` 保护共享状态
- SSE 超时：5 分钟自动断开，防止资源泄漏
- 资源泄漏：修复 `auth_manager.py` 中多余 page 未关闭
- 模块副作用：移除导入时自动执行的代码

**重构**
- 配置统一：合并 `paths.py` 到 `config.py`
- 路由拆分：`routes.py` → `health.py` + `videos.py` + `sync.py`
- 任务管理：`threading.Thread` → `asyncio.create_task`
- 删除未使用代码：`verify_auth()`、`SYNC_PROGRESS_FILE`

#### 前端

**新增**
- Tailwind CSS 支持
- 组件化架构：`Layout` + `SyncPanel` + `VideoTable`
- API 封装：`client.ts`（使用 Vite proxy）
- SSE Hook：`useSync.ts`（自动清理连接）

**修复**
- SSE 内存泄漏：EventSource 组件卸载时正确关闭
- TypeScript 错误：修复类型导入和接口定义
- API 地址：移除硬编码，使用 Vite proxy

**重构**
- App.tsx 从 398 行拆分为 5 个独立模块
- 内联样式改为 Tailwind 类
- 使用 `types/index.ts` 中的类型定义

**删除**
- 未使用依赖：`axios`、`lucide-react`
- 废弃文件：`App.css`、`assets/`

#### 文档

- 新增 `AGENTS.md`：项目架构和开发指南
- 新增 `USER_GUIDE.md`：用户使用手册
- 新增 `TEST_CHECKLIST.md`：测试清单
- 新增 `changelog/`：更新日志

---

## [1.0.0] - 2026-06-03

### 初始版本

首个可用版本，实现基本功能。

#### 功能
- 抖音收藏视频抓取（Playwright）
- 登录态管理（扫码登录）
- 视频列表展示
- SSE 实时同步进度
- JSON 文件存储
