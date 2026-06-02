@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo ========================================
echo   Douyin Knowledge Base - Start Script
echo ========================================
echo.

cd /d "%~dp0"

echo [1/6] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.11+
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python found

echo [2/6] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found. Please install Node.js 18+
    echo Download: https://nodejs.org/
    pause
    exit /b 1
)
echo [OK] Node.js found

echo [3/6] Checking backend virtual environment...
if not exist "backend\venv" (
    echo [INFO] Creating virtual environment...
    cd backend
    python -m venv venv
    cd ..
)
echo [OK] Virtual environment ready

echo [4/6] Installing backend dependencies...
cd backend
call venv\Scripts\activate.bat
pip install -r requirements.txt -q
if errorlevel 1 (
    echo [ERROR] Backend dependencies installation failed
    pause
    exit /b 1
)
cd ..
echo [OK] Backend dependencies installed

echo [5/6] Checking Playwright browser...
cd backend
call venv\Scripts\activate.bat
python -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); b = p.chromium.launch(headless=True); b.close(); p.stop()" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing Playwright Chromium...
    playwright install chromium
)
cd ..
echo [OK] Playwright browser ready

echo [6/6] Installing frontend dependencies...
if not exist "frontend\node_modules" (
    cd frontend
    npm install
    cd ..
)
echo [OK] Frontend dependencies installed

echo.
echo ========================================
echo   All dependencies checked!
echo ========================================
echo.

echo [INFO] Checking Ollama service...
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Ollama service not running
    echo [INFO] To use local AI model:
    echo   1. Download Ollama from https://ollama.ai
    echo   2. Run 'ollama serve'
    echo   3. Run 'ollama pull qwen2.5:14b'
    echo.
    echo [INFO] To use cloud API, edit backend\.env:
    echo   AI_PROVIDER=openai or AI_PROVIDER=deepseek
    echo   OPENAI_API_KEY=your_key or DEEPSEEK_API_KEY=your_key
    echo.
) else (
    echo [OK] Ollama service running
)

echo ========================================
echo   Starting services...
echo ========================================
echo.

echo [START] Backend server (port 8000)...
start "DouyinKB-Backend" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate.bat && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 3 /nobreak >nul

echo [START] Frontend server (port 5173)...
start "DouyinKB-Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ========================================
echo   Services started!
echo ========================================
echo.
echo   Frontend: http://localhost:5173
echo   Backend:  http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo.
echo   Press any key to open browser...
pause >nul

start http://localhost:5173

echo.
echo [INFO] Close this window will NOT stop services
echo [INFO] To stop services, close the backend and frontend windows
echo.
pause
