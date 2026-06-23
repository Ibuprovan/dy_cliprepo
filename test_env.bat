@echo off
chcp 65001 >nul 2>&1

echo.
echo ========================================
echo   Quick Test - Check if services work
echo ========================================
echo.

cd /d "%~dp0"

echo [1] Testing Python...
python --version
if errorlevel 1 (
    echo [FAIL] Python not found
    pause
    exit /b 1
)
echo [OK]
echo.

echo [2] Testing backend venv activation...
if not exist "backend\venv\Scripts\activate.bat" (
    echo Creating venv...
    cd backend
    python -m venv venv
    cd ..
)
cd backend
call venv\Scripts\activate.bat
echo [OK]
echo.

echo [3] Testing playwright import...
python -c "from playwright.async_api import async_playwright; print('Playwright OK')"
if errorlevel 1 (
    echo Installing playwright...
    pip install playwright
    playwright install chromium
)
cd ..
echo [OK]
echo.

echo [4] Testing auth module...
cd backend
call venv\Scripts\activate.bat
python -c "from app.scraper.auth import main; print('Auth module OK')"
if errorlevel 1 (
    echo [FAIL] Auth module import error
    cd ..
    pause
    exit /b 1
)
cd ..
echo [OK]
echo.

echo ========================================
echo   All tests passed!
echo   You can now run login.bat
echo ========================================
echo.
pause
