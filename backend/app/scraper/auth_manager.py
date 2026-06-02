import os
import json
from typing import Optional

from app.config import settings


class AuthManager:
    def __init__(self):
        self.cookie_path = os.path.join(settings.AUTH_DIR, "douyin_cookies.json")
        os.makedirs(settings.AUTH_DIR, exist_ok=True)

    def is_logged_in(self) -> bool:
        return os.path.exists(self.cookie_path) and os.path.getsize(self.cookie_path) > 0

    def save_cookies(self, cookies: list) -> None:
        with open(self.cookie_path, "w", encoding="utf-8") as f:
            json.dump(cookies, f, ensure_ascii=False, indent=2)

    def load_cookies(self) -> Optional[list]:
        if not self.is_logged_in():
            return None
        try:
            with open(self.cookie_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def clear_cookies(self) -> None:
        if os.path.exists(self.cookie_path):
            os.remove(self.cookie_path)

    async def manual_login(self, on_complete=None) -> dict:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()

            await page.goto("https://www.douyin.com")

            return {
                "status": "waiting",
                "message": "浏览器已打开，请使用抖音APP扫码登录。登录完成后请调用 /api/auth/confirm 接口。",
                "browser": browser,
                "context": context,
            }

    async def load_auth_context(self, browser) -> object:
        from playwright.async_api import Browser

        context = await browser.new_context()
        cookies = self.load_cookies()
        if cookies:
            await context.add_cookies(cookies)
        return context


auth_manager = AuthManager()
