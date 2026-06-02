@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

cd /d "%~dp0"

echo [1/6] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    pause
    exit /b 1
)

echo [2/6] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found
    pause
    exit /b 1
)

echo [3/6] Checking backend virtual environment...
if not exist "backend\venv" (
    cd backend
    python -m venv venv
    cd ..
)

echo [4/6] Installing backend dependencies...
cd backend
call venv\Scripts\activate.bat
pip install -r requirements.txt -q
cd ..

echo [5/6] Checking Playwright browser...
cd backend
call venv\Scripts\activate.bat
python -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); b = p.chromium.launch(headless=True); b.close(); p.stop()" >nul 2>&1
if errorlevel 1 (
    playwright install chromium
)
cd ..

echo [6/6] Installing frontend dependencies...
if not exist "frontend\node_modules" (
    cd frontend
    npm install
    cd ..
)

echo.
echo ========================================
echo   Services starting...
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
echo   Please open http://localhost:5173 in your browser manually.
echo.
pause
