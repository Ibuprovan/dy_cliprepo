@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo.
echo ========================================
echo   Douyin Favorites AI - Startup Script
echo ========================================
echo.

cd /d "%~dp0"
echo Current directory: %CD%
echo.

REM Create log directory
if not exist "backend\data\logs" mkdir "backend\data\logs"

REM Check Python
echo [1/6] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [FAIL] Python not found!
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    echo.
    pause
    goto :end
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python version: %PYTHON_VERSION%
echo.

REM Check Node.js
echo [2/6] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [FAIL] Node.js not found!
    echo Please install Node.js 18+ from https://nodejs.org/
    echo.
    pause
    goto :end
)
for /f %%i in ('node --version 2^>^&1') do set NODE_VERSION=%%i
echo [OK] Node.js version: %NODE_VERSION%
echo.

REM Check and create backend virtual environment
echo [3/6] Checking backend environment...
if not exist "backend\venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    cd backend
    python -m venv venv >> "data\logs\start.log" 2>&1
    if errorlevel 1 (
        echo [FAIL] Failed to create virtual environment!
        echo Check log: backend\data\logs\start.log
        pause
        goto :end
    )
    cd ..
)
echo [OK] Virtual environment ready
echo.

REM Install backend dependencies
echo [4/6] Installing backend dependencies...
cd backend
call venv\Scripts\activate.bat
pip install -r requirements.txt -q >> "data\logs\start.log" 2>&1
if errorlevel 1 (
    echo [FAIL] Backend dependencies installation failed!
    echo Check log: backend\data\logs\start.log
    cd ..
    pause
    goto :end
)
cd ..
echo [OK] Backend dependencies installed
echo.

REM Check and install frontend dependencies
echo [5/6] Checking frontend environment...
if not exist "frontend\node_modules" (
    echo Installing frontend dependencies...
    cd frontend
    call npm install >> "..\backend\data\logs\start.log" 2>&1
    if errorlevel 1 (
        echo [FAIL] Frontend dependencies installation failed!
        echo Check log: backend\data\logs\start.log
        pause
        goto :end
    )
    cd ..
)
echo [OK] Frontend dependencies ready
echo.

REM Check auth state
echo [6/6] Checking auth state...
if exist "backend\data\douyin_auth.json" (
    echo [OK] Auth file found
) else (
    echo.
    echo [WARNING] Auth file not found!
    echo You must login before syncing.
    echo.
    set /p DO_LOGIN="Run login now? (Y/N): "
    if /i "!DO_LOGIN!"=="Y" (
        echo Starting login...
        cd backend
        call venv\Scripts\activate.bat
        python login_manual.py
        cd ..
        if not exist "backend\data\douyin_auth.json" (
            echo [FAIL] Login failed or cancelled!
            echo You can login later: start_login.bat
            echo.
        ) else (
            echo [OK] Login successful
        )
    ) else (
        echo Skipping login. You can login later: start_login.bat
    )
    echo.
)
echo.

echo ========================================
echo   Starting services...
echo ========================================
echo.

REM Start backend in new window
echo Starting backend on port 8000...
cd backend
start "Backend" cmd /k "call venv\Scripts\activate.bat && python run_server.py"
cd ..
echo [OK] Backend starting...

REM Wait for backend to start
echo Waiting for backend...
timeout /t 5 /nobreak >nul

REM Start frontend in new window
echo Starting frontend on port 5173...
cd frontend
start "Frontend" cmd /k "npm run dev"
cd ..
echo [OK] Frontend starting...

REM Wait for frontend to start
echo Waiting for frontend...
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo   All services started!
echo ========================================
echo.
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:5173
echo   API Docs: http://localhost:8000/docs
echo.
echo   Open http://localhost:5173 to use.
echo.
echo   DO NOT CLOSE THIS WINDOW!
echo ========================================
echo.

REM Open browser
start "" "http://localhost:5173"

REM Keep window open
pause >nul

:end
endlocal
