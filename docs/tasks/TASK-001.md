# TASK-001: 全项目 Bug 与逻辑漏洞排查

- 类型: DEBUG + REFACTOR
- 状态: DONE
- 负责人: PMO → explore → reviewer
- 创建时间: 2026-06-24
- 完成时间: 2026-06-28

## 修复汇总（共 18 个问题）

### 严重安全漏洞（3 个，全部修复）
| # | 文件 | 问题 | 修复方式 |
|---|------|------|----------|
| 1 | video_repo.py + videos.py | SQL 注入：列名未校验 | ALLOWED_COLUMNS 白名单 + VideoUpdate 模型 |
| 2 | main.py | 路径穿越：SPA 可读任意文件 | resolve() + 前缀检查 |
| 3 | task_repo.py | SQL 拼接风险 | ALLOWED_TASK_COLUMNS 白名单 |

### 功能缺陷（9 个，全部修复）
| # | 文件 | 问题 | 修复方式 |
|---|------|------|----------|
| 4 | main.py | SPA catch-all 吞掉 API 404 | 排除 /api/ 和 /health 路径 |
| 5 | App.tsx | 错误启动命令提示 | 改为 python run_server.py |
| 6 | video_repo.py | JSON 解析无容错 | _safe_json_loads 函数 |
| 7 | client.ts + useSync.ts | SSE 断连静默关闭 | 增加 onError 回调 |
| 8 | App.tsx | 错误被完全吞掉 | 添加 console.error |
| 9 | useSync.ts | cancelled 状态映射错误 | statusMap 正确映射 |
| 10 | sync.py | SSE 超时 5 分钟太短 | 改为 30 分钟 |
| 11 | index.css | CSS reset 与 Tailwind 冲突 | 删除手动 reset |
| 12 | main.py | 热重载丢失事件循环策略 | main.py 中也设置 ProactorEventLoop |

### 同步致命问题（1 个，核心修复）
| # | 文件 | 问题 | 修复方式 |
|---|------|------|----------|
| - | sync_service.py | Playwright NotImplementedError | 改用 threading 独立线程方案 |

### 代码质量（4 个，全部修复）
| # | 文件 | 问题 | 修复方式 |
|---|------|------|----------|
| 14 | videos.py | 未使用的导入 | 删除 generate_summary 导入 |
| 17 | database.py | 单例连接无健康检查 | SELECT 1 检查 + 自动重连 |
| 18 | sync_service.py | 异步函数中同步 I/O | asyncio.to_thread |
| 19 | sync.py | 类型注解不正确 | Optional[str] |
| 20 | start.bat | 依赖安装失败继续执行 | 失败时中止 |
| 13 | video_service.py | 未使用函数，逻辑重复 | 已删除整个文件 |

### 启动脚本改进
| 文件 | 修改 |
|------|------|
| start.bat | 全英文输出、登录态检查、自动引导登录、防闪退 |
| start_backend.bat | 改用 run_server.py |
| login.bat | 改用 login_manual.py |
| start_login.bat | 新增独立登录脚本 |

### 未修复（轻微，可后续处理）
| # | 文件 | 问题 | 原因 |
|---|------|------|------|
| 15 | types/index.ts | 前后端类型不一致 | 不影响功能 |
| 16 | login_manual.py | sys.path.insert 脆弱 | 需要项目结构调整 |
