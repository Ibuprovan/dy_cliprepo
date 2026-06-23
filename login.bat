@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo.
echo ========================================
echo   抖音登录 - 扫码登录工具
echo ========================================
echo.

cd /d "%~dp0"
echo Current directory: %CD%
echo.

echo [1/3] Checking Python...
python --version 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Python not found!
    echo Please install Python 3.11+ from https://www.python.org
    echo.
    pause
    exit /b 1
)
echo [OK] Python found
echo.

echo [2/3] Checking virtual environment...
if not exist "backend\venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    cd backend
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create venv
        pause
        exit /b 1
    )
    cd ..
)
echo [OK] Virtual environment ready
echo.

echo [3/3] Checking Playwright...
cd backend
call venv\Scripts\activate.bat
python -c "import playwright" 2>nul
if errorlevel 1 (
    echo Installing playwright...
    pip install playwright -q
    playwright install chromium
)
echo [OK] Playwright ready
echo.

echo ========================================
echo   Starting login process...
echo   A browser will open, scan QR code.
echo ========================================
echo.

python -m app.scraper.auth
if errorlevel 1 (
    echo.
    echo [ERROR] Login script failed!
    echo.
)

cd ..
echo.
echo ========================================
echo   Process finished.
echo ========================================
echo.
pause
