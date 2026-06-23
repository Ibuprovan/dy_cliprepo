@echo off
chcp 65001 >nul 2>&1

cd /d "%~dp0frontend"

echo.
echo ========================================
echo   启动前端服务
echo ========================================
echo.

echo 当前目录: %CD%
echo.

if not exist "node_modules" (
    echo 安装依赖...
    call npm install
    echo.
)

echo 启动前端服务 (端口 5173)...
echo 按 Ctrl+C 停止
echo.

call npm run dev

pause
