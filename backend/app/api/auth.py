from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import asyncio
import json

from app.services.sync_service import sync_service
from app.scraper.auth_manager import auth_manager

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/status")
async def auth_status():
    logged_in = auth_manager.is_logged_in()
    return {
        "logged_in": logged_in,
        "message": "已登录" if logged_in else "未登录，请先扫码登录",
    }


@router.post("/login")
async def login():
    if auth_manager.is_logged_in():
        return {"status": "already_logged_in", "message": "已登录"}

    result = await sync_service.manual_login()
    return result


@router.post("/confirm")
async def confirm_login():
    result = await sync_service.confirm_login()
    return result


@router.post("/logout")
async def logout():
    auth_manager.clear_cookies()
    return {"status": "success", "message": "已退出登录"}
