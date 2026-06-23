# 抖音收藏 AI 知识库 - 用户指南

## 快速开始

### 环境要求

- Windows 10/11
- Python 3.11+
- Node.js 18+

### 首次安装

```bash
# 1. 克隆仓库
git clone https://github.com/Ibuprovan/dy_cliprepo.git
cd dy_cliprepo

# 2. 一键启动（自动安装依赖）
start.bat
```

### 登录抖音

首次使用需要扫码登录：

```bash
login.bat
```

1. 在弹出的浏览器中用抖音 APP 扫码
2. 登录成功后在命令行窗口按回车
3. 登录态保存在 `backend/data/douyin_auth.json`

> 登录态有效期约 7 天，过期后需重新登录。

---

## 日常使用

### 启动服务

```bash
start.bat
```

启动后访问：
- 前端：http://localhost:5173
- API 文档：http://localhost:8000/docs

### 同步收藏

1. 打开 http://localhost:5173
2. 点击「开始同步」
3. 等待同步完成

### 浏览视频

同步完成后，在视频列表中：
- 查看标题、作者、AI 总结
- 点击「打开链接」跳转到抖音原视频

---

## 常见问题

### Q: 后端启动失败

**症状**：前端显示「后端服务未启动」

**解决**：
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run_server.py
```

### Q: 同步失败 - 登录态错误

**症状**：提示「请先运行 login_manual.py」

**解决**：
```bash
login.bat
```

### Q: Playwright 浏览器启动失败

**症状**：提示「启动浏览器失败」

**解决**：
```bash
cd backend
venv\Scripts\activate
playwright install chromium
```

### Q: 端口被占用

**症状**：启动后无法访问

**解决**：关闭占用 8000 或 5173 端口的程序，或修改配置。

---

## 文件说明

```
dy_cliprepo/
├── start.bat              # 一键启动
├── login.bat              # 登录抖音
├── start_backend.bat      # 单独启动后端
├── start_frontend.bat     # 单独启动前端
└── backend/
    └── data/              # 运行时数据
        ├── app.db         # SQLite 数据库
        └── douyin_auth.json  # 登录态
```

---

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| POST | `/api/sync/start` | 启动同步 |
| POST | `/api/sync/stop` | 停止同步 |
| GET | `/api/sync/status/{task_id}` | 同步状态 (SSE) |
| GET | `/api/videos` | 视频列表 |
| GET | `/api/videos/{id}` | 视频详情 |
| PUT | `/api/videos/{id}` | 更新视频 |
| DELETE | `/api/videos/{id}` | 删除视频 |
| GET | `/api/videos/categories` | 所有分类 |

完整文档：http://localhost:8000/docs

---

## 技术栈

- **后端**：Python FastAPI + SQLite + Playwright
- **前端**：React 19 + TypeScript + Tailwind CSS + Vite
- **数据**：本地 SQLite，无外部依赖
