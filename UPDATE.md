# 更新日志

记录项目的功能改进、bug 修复和安全更新。

---

## 2026-06-28

### AI 摘要质量全面修复

**问题**：大量视频的 AI 摘要质量差，表现为：

- 摘要只是 desc 前 100 字的生硬截取
- 分类几乎全部为"未分类"
- 429 限流时直接放弃，无重试
- 短描述走 VL 模式但视频 URL 不可访问导致超时

**根因**：

- `ai_service.py` 中 `_fallback_summary` 是 `desc[:100]`（截取而非总结）
- GLM API 遇到 429 立即 `raise_for_status` 抛错，没有重试
- `use_vl = bool(video_url and len(desc.strip()) < 50)` 门槛过低，短描述全部走 VL
- 分类匹配依赖 AI 输出，AI 失败后只剩"其他"或"未分类"

**修复**：

| 改进 | 位置 |
|------|------|
| 新增 `_call_with_retry`：429/超时自动重试 3 次，间隔 2/4/6s 递增 | [ai_service.py:87](backend/app/services/ai_service.py#L87) |
| 重新设计路由：仅当 desc 完全为空才走 VL | [ai_service.py:121](backend/app/services/ai_service.py#L121) |
| 新增 `_local_fallback`：智能提取（清理 hashtag + 按句分段）+ 关键词本地分类 | [ai_service.py:263](backend/app/services/ai_service.py#L263) |
| 关键词表扩充：新增数学建模/装修/职场/面试/求职/婚姻/前端/开源 | [ai_service.py:228](backend/app/services/ai_service.py#L228) |
| API Key 缺失时走本地兜底（而非返回"未分类"） | [ai_service.py:111](backend/app/services/ai_service.py#L111) |
| `.env.example` 对齐实际代码：ZHIPUAI_* 配置 | [backend/.env.example](backend/.env.example) |

**效果**：11 条历史视频重新生成后，AI 成功摘要 9/11，分类命中 11/11，过短摘要 0/11。

---

### 同步后"全部"分类无法加载

**问题**：同步完成后，依次点击具体分类 → "全部"，视频列表清空。

**根因**：[App.tsx](frontend/src/App.tsx) 的 `handleCategoryChange` 收到 `'全部'` 后直接 `setSelectedCategory('全部')` 并 `loadVideos('全部')`，后端按字面值 `?category=全部` 过滤自然零结果。

**修复**：[App.tsx:33-37](frontend/src/App.tsx#L33-L37) 把 `'全部'` 归一化为空串，触发 `loadVideos(undefined)` 请求全部分类。

---

### Bug 与安全审计 + 修复（15 项）

**后端安全**：

| Bug | 修复 |
|-----|------|
| 后端绑定 `0.0.0.0` 暴露整个局域网 | [config.py:74](backend/app/core/config.py#L74) 改为 `127.0.0.1` |
| `?limit=999999` 无上限 | [sync.py:44-45](backend/app/api/v1/sync.py#L44-L45) 钳制为 `MAX_SYNC_LIMIT` |

**后端任务状态**：

| Bug | 修复 |
|-----|------|
| 重启后僵尸 running 任务永远阻塞新同步 | [main.py:38](backend/app/main.py#L38) 启动时调用 `cleanup_zombie_tasks()` |
| 用户取消被 `complete_task` 覆盖为 completed | [sync_service.py:171-176](backend/app/services/sync_service.py#L171-L176) 用 `was_cancelled` 标记 |
| `limit=0` 时 `videos_saved / limit` 除零 | [sync_service.py:131](backend/app/services/sync_service.py#L131) `max(len(new_videos), 1)` |
| 全重复视频时进度永远卡 0% | [sync_service.py:164-168](backend/app/services/sync_service.py#L164-L168) 用 `total_to_process` 替代 `limit` |
| `fail_task` 自身失败致任务卡 running | [sync_service.py:217-222](backend/app/services/sync_service.py#L217-L222) 新增 `_safe_fail_task` 包装 |

**后端爬虫**：

| Bug | 修复 |
|-----|------|
| 单个详情页 `new_page` 失败中止整条同步 | [sync_engine.py:486-499](backend/app/scraper/sync_engine.py#L486-L499) 捕获后跳过该视频 |

**后端 API**：

| Bug | 修复 |
|-----|------|
| SSE 生成器无 DB 异常保护，连接静默中断 | [sync.py:87-94](backend/app/api/v1/sync.py#L87-L94) 异常时推送错误事件 |

**前端状态管理**：

| Bug | 修复 |
|-----|------|
| `start` 重复调用致 EventSource 泄漏 | [useSync.ts:46-47](frontend/src/hooks/useSync.ts#L46-L47) 开头 `cleanup()` + 赋值前再清理 |
| SSE 字段缺失导致 `undefined%` 渲染 | [useSync.ts:104-105](frontend/src/hooks/useSync.ts#L104-L105) `?? 0` 兜底 |
| 切换分类后 `selectedIds`/`imgErrors`/`expandedTitles` 残留 | [VideoTable.tsx:36-40](frontend/src/components/VideoTable.tsx#L36-L40) `useEffect` 监听 `videos` 清理 |
| `allSelected` 用 size 比较致全选状态误判 | [VideoTable.tsx:50](frontend/src/components/VideoTable.tsx#L50) 改用 `videos.every(...)` 内容比较 |

**前端 UI**：

| Bug | 修复 |
|-----|------|
| 移动端复选框 absolute 定位错乱（跑到页面左上） | [VideoTable.tsx:158](frontend/src/components/VideoTable.tsx#L158) 卡片容器加 `relative` |
| Firefox 下载 Markdown 静默失败 | [VideoTable.tsx:20-25](frontend/src/components/VideoTable.tsx#L20-L25) `appendChild` + 延迟 `revokeObjectURL` |

**前端数据流**：

| Bug | 修复 |
|-----|------|
| 删除视频后分类列表不刷新，空分类残留 | [App.tsx:133-137](frontend/src/App.tsx#L133-L137) `onVideosChange` 同步调用 `getCategories()` |

---

## 提交历史

```
feat: 重写 AI 摘要：429 重试 + 智能 fallback + 本地分类
fix: 修复同步后点击"全部"分类无法加载视频
fix: 15 项 bug 与安全修复
docs: 添加 UPDATE.md 更新日志
```
