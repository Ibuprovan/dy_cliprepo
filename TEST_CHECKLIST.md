# 抖音收藏AI知识库 - 测试清单

## 1. 环境检查

### 1.1 Python版本
```bash
python --version
# 预期：Python 3.10+
```

### 1.2 Node.js版本
```bash
node --version
# 预期：v18+
```

### 1.3 npm版本
```bash
npm --version
# 预期：9+
```

## 2. 诊断脚本

运行环境诊断脚本，检查所有前置条件：
```bash
cd backend
python diagnose.py
```

**预期输出：**
- 所有检查项显示 `[PASS]`
- 如果有 `[FAIL]` 项，按照提示修复

## 3. 登录测试

### 3.1 运行登录脚本
```bash
cd backend
python login_manual.py
```

### 3.2 预期现象
1. 弹出浏览器窗口，显示抖音首页
2. 在浏览器中扫码登录
3. 登录成功后，在命令行窗口按回车
4. 显示 "✓ 登录态已保存到 data\douyin_auth.json"
5. 文件大小 > 100 bytes

### 3.3 验证登录态
```bash
# 检查文件是否存在
dir backend\data\douyin_auth.json
```

## 4. 同步测试

### 4.1 运行同步测试脚本
```bash
cd backend
python test_sync.py
```

### 4.2 预期现象
1. 显示 "开始拉取收藏（限制1条）..."
2. 等待30秒左右
3. 显示成功获取的视频信息（标题、作者、URL）
4. 显示 "✓ 测试成功！"

### 4.3 如果失败
- 检查日志：`backend\data\logs\sync.log`
- 确认登录态是否有效：重新运行 `python login_manual.py`

## 5. 端到端测试

### 5.1 启动服务
1. 双击 `start.bat`
2. 观察是否打开两个命令行窗口（Backend 和 Frontend）
3. 等待服务启动完成

### 5.2 访问前端
1. 浏览器自动打开 http://localhost:5173
2. 页面应显示 "抖音收藏AI知识库" 标题
3. 如果显示红色警告 "后端服务未启动"，等待几秒后刷新

### 5.3 测试同步功能
1. 点击 "开始同步" 按钮
2. 观察进度条和当前处理的视频标题
3. 等待同步完成
4. 视频列表应显示同步的视频

### 5.4 测试视频链接
1. 在视频列表中点击 "打开链接"
2. 应在新标签页打开抖音视频页面

## 6. 常见问题排查

### 6.1 启动脚本闪退
**症状：** 双击 `start.bat` 后窗口立即关闭

**排查步骤：**
1. 用命令行手动运行：
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --port 8000
   ```
2. 查看错误信息
3. 检查日志：`data\logs\start.log`

**常见原因：**
- Python未安装或未加入PATH
- 虚拟环境损坏：删除 `backend\venv` 重新运行 `start.bat`
- 端口被占用：关闭占用8000或5173端口的程序

### 6.2 同步失败：无法启动浏览器
**症状：** 点击同步后显示 "同步错误: 启动浏览器失败"

**排查步骤：**
1. 运行诊断脚本：`cd backend && python diagnose.py`
2. 检查Playwright浏览器是否安装：
   ```bash
   python -m playwright install chromium
   ```
3. 检查日志：`backend\data\logs\sync.log`

**常见原因：**
- Playwright浏览器未安装
- 系统缺少依赖库（Windows通常不需要）

### 6.3 同步失败：登录态失效
**症状：** 显示 "登录态错误" 或 "请先运行 login_manual.py"

**排查步骤：**
1. 检查登录态文件是否存在：
   ```bash
   dir backend\data\douyin_auth.json
   ```
2. 重新登录：
   ```bash
   cd backend
   python login_manual.py
   ```

**常见原因：**
- 登录态过期（抖音cookies有效期约7天）
- 登录态文件损坏

### 6.4 前端白屏
**症状：** 浏览器打开后显示空白页面

**排查步骤：**
1. 打开浏览器开发者工具（F12）
2. 查看Console面板的错误信息
3. 查看Network面板是否有请求失败

**常见原因：**
- 后端未启动：检查 http://localhost:8000 是否可访问
- CORS错误：确认后端日志
- 前端编译错误：检查 `frontend\npm run dev` 输出

### 6.5 同步没有结果
**症状：** 同步完成但视频列表为空

**排查步骤：**
1. 检查抖音账号是否有收藏
2. 检查日志：`backend\data\logs\sync.log`
3. 尝试手动运行同步测试：
   ```bash
   cd backend
   python test_sync.py
   ```

**常见原因：**
- 抖音收藏为空
- 页面结构变化（需要更新选择器）
- 登录态无效

## 7. 数据文件说明

| 文件路径 | 说明 |
|---------|------|
| `backend\data\douyin_auth.json` | 抖音登录态（storage_state） |
| `backend\data\videos.json` | 同步的视频数据 |
| `backend\data\logs\sync.log` | 同步日志 |
| `backend\data\logs\start.log` | 启动日志 |

## 8. 重新开始

如果需要完全重置：

1. 删除数据目录：
   ```bash
   rmdir /s /q backend\data
   ```

2. 删除虚拟环境：
   ```bash
   rmdir /s /q backend\venv
   ```

3. 删除前端依赖：
   ```bash
   rmdir /s /q frontend\node_modules
   ```

4. 重新运行 `start.bat`
