@echo off
chcp 65001 >nul 2>&1

echo.
echo ========================================
echo   Environment Check
echo ========================================
echo.

cd /d "%~dp0"
echo Current directory: %CD%
echo.

echo --- Python ---
python --version 2>&1
echo.

echo --- Node.js ---
node --version 2>&1
echo.

echo --- pip ---
pip --version 2>&1
echo.

echo --- npm ---
call npm --version 2>&1
echo.

echo --- Backend venv ---
if exist "backend\venv\Scripts\activate.bat" (
    echo [OK] venv exists
) else (
    echo [NOT FOUND] venv not found
)
echo.

echo --- Auth file ---
if exist "backend\data\auth.json" (
    echo [OK] auth.json exists
) else (
    echo [NOT FOUND] auth.json not found
)
echo.

echo --- Frontend node_modules ---
if exist "frontend\node_modules" (
    echo [OK] node_modules exists
) else (
    echo [NOT FOUND] node_modules not found
)
echo.

echo ========================================
echo   Done.
echo ========================================
echo.
pause
