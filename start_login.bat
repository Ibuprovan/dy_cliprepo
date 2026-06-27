@echo off
chcp 65001 >nul 2>&1
setlocal

echo.
echo ========================================
echo   Douyin Login - Scan QR Code
echo ========================================
echo.

cd /d "%~dp0"

REM Check venv
if not exist "backend\venv\Scripts\activate.bat" (
    echo [FAIL] Virtual environment not found!
    echo Please run start.bat first to set up the environment.
    echo.
    pause
    goto :end
)

REM Run login
cd backend
call venv\Scripts\activate.bat
echo Starting login process...
echo A browser will open. Scan the QR code to login.
echo.
python login_manual.py

if exist "data\douyin_auth.json" (
    echo.
    echo [OK] Login successful! Auth saved.
    echo You can now run start.bat to start the service.
) else (
    echo.
    echo [FAIL] Login failed or cancelled.
)

cd ..
echo.
pause

:end
endlocal
