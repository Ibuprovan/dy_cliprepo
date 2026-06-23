# backend/run_server.py
"""
后端服务启动脚本
解决Windows平台Playwright与uvicorn的asyncio兼容性问题
运行方式：cd backend && python run_server.py
"""

import sys
import asyncio

# Windows兼容性修复：必须使用ProactorEventLoop才能创建子进程
# Playwright需要创建子进程来启动浏览器
# SelectorEventLoop不支持子进程，必须使用ProactorEventLoop（Windows默认）
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
