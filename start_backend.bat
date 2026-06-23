@echo off
chcp 65001 >nul 2>&1

cd /d "%~dp0"

echo.
echo ========================================
echo   启动后端服务
echo ========================================
echo.

echo 当前目录: %CD%
echo.

echo 激活虚拟环境...
call "%~dp0backend\venv\Scripts\activate.bat"

echo.
echo 启动后端服务 (端口 8000)...
echo 按 Ctrl+C 停止
echo.

python -m uvicorn app.main:app --reload --port 8000

pause
