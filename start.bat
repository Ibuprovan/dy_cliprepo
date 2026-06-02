@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo   抖音收藏 AI 知识库 - 启动脚本
echo ========================================
echo.

:: 获取脚本所在目录
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: 检查 Python
echo [1/6] 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.11+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [通过] Python %PYTHON_VERSION%

:: 检查 Node.js
echo [2/6] 检查 Node.js 环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Node.js，请先安装 Node.js 18+
    echo 下载地址: https://nodejs.org/
    pause
    exit /b 1
)
for /f %%i in ('node --version') do set NODE_VERSION=%%i
echo [通过] Node.js %NODE_VERSION%

:: 检查后端虚拟环境
echo [3/6] 检查后端虚拟环境...
if not exist "backend\venv" (
    echo [信息] 创建虚拟环境...
    cd backend
    python -m venv venv
    cd ..
)
echo [通过] 虚拟环境就绪

:: 安装后端依赖
echo [4/6] 安装后端依赖...
cd backend
call venv\Scripts\activate.bat
pip install -r requirements.txt -q
if errorlevel 1 (
    echo [错误] 后端依赖安装失败
    pause
    exit /b 1
)
cd ..
echo [通过] 后端依赖安装完成

:: 安装 Playwright 浏览器
echo [5/6] 检查 Playwright 浏览器...
cd backend
call venv\Scripts\activate.bat
python -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); b = p.chromium.launch(headless=True); b.close(); p.stop()" >nul 2>&1
if errorlevel 1 (
    echo [信息] 安装 Playwright Chromium...
    playwright install chromium
)
cd ..
echo [通过] Playwright 浏览器就绪

:: 安装前端依赖
echo [6/6] 安装前端依赖...
if not exist "frontend\node_modules" (
    cd frontend
    npm install -q
    cd ..
)
echo [通过] 前端依赖安装完成

echo.
echo ========================================
echo   所有依赖检查完成！
echo ========================================
echo.

:: 检查 Ollama
echo [信息] 检查 Ollama 服务...
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo [警告] Ollama 服务未启动
    echo [提示] 如需使用本地 AI 模型，请：
    echo   1. 访问 https://ollama.ai 下载安装 Ollama
    echo   2. 运行 'ollama serve' 启动服务
    echo   3. 运行 'ollama pull qwen2.5:14b' 拉取模型
    echo.
    echo [提示] 如需使用云端 API，请在 backend\.env 文件中配置：
    echo   AI_PROVIDER=openai 或 AI_PROVIDER=deepseek
    echo   OPENAI_API_KEY=your_key 或 DEEPSEEK_API_KEY=your_key
    echo.
) else (
    echo [通过] Ollama 服务已启动
)

echo ========================================
echo   启动服务...
echo ========================================
echo.

:: 启动后端
echo [启动] 后端服务 (端口 8000)...
start "抖音知识库-后端" cmd /k "cd /d %SCRIPT_DIR%backend && call venv\Scripts\activate.bat && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

:: 等待后端启动
timeout /t 3 /nobreak >nul

:: 启动前端
echo [启动] 前端服务 (端口 5173)...
start "抖音知识库-前端" cmd /k "cd /d %SCRIPT_DIR%frontend && npm run dev"

echo.
echo ========================================
echo   服务启动完成！
echo ========================================
echo.
echo   前端地址: http://localhost:5173
echo   后端地址: http://localhost:8000
echo   API 文档: http://localhost:8000/docs
echo.
echo   按任意键打开浏览器...
pause >nul

:: 打开浏览器
start http://localhost:5173

echo.
echo [提示] 关闭此窗口不会停止服务
echo [提示] 如需停止服务，请关闭"抖音知识库-后端"和"抖音知识库-前端"窗口
echo.
pause
