import asyncio
import os
import random
from typing import Callable, Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

from app.config import settings
from app.scraper.auth_manager import auth_manager


class DouyinScraper:
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self._playwright = None
        self._login_mode = False

    async def start(self, headless: bool = True):
        try:
            self._playwright = await async_playwright().start()
            
            # 强制使用 Chromium
            self.browser = await self._playwright.chromium.launch(
                headless=headless,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            self.context = await self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            )

            cookies = auth_manager.load_cookies()
            if cookies:
                await self.context.add_cookies(cookies)

            self.page = await self.context.new_page()
            return True
        except Exception as e:
            print(f"Failed to start browser: {e}")
            await self.stop()
            return False

    async def stop(self):
        try:
            if self.page:
                await self.page.close()
        except Exception:
            pass
        try:
            if self.context:
                await self.context.close()
        except Exception:
            pass
        try:
            if self.browser:
                await self.browser.close()
        except Exception:
            pass
        try:
            if self._playwright:
                await self._playwright.stop()
        except Exception:
            pass
        self.browser = None
        self.context = None
        self.page = None
        self._playwright = None
        self._login_mode = False

    async def check_login_status(self) -> bool:
        if not self.page:
            return False

        try:
            await self.page.goto("https://www.douyin.com", wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(3)

            # 检查是否已登录
            user_info = await self.page.query_selector('[data-e2e="user-info"]')
            if user_info:
                return True

            # 检查是否有登录按钮
            login_btn = await self.page.query_selector('[data-e2e="login-button"]')
            if login_btn:
                return False

            # 检查页面内容
            content = await self.page.content()
            if '登录' in content or 'login' in content.lower():
                return False

            return False
        except Exception as e:
            print(f"Check login status failed: {e}")
            return False

    async def manual_login(self) -> dict:
        # 先关闭之前的浏览器
        await self.stop()

        try:
            success = await self.start(headless=False)
            if not success:
                return {
                    "status": "error",
                    "message": "启动浏览器失败，请检查 Playwright 是否正确安装",
                }
            
            self._login_mode = True

            # 导航到抖音
            await self.page.goto("https://www.douyin.com", wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(2)

            return {
                "status": "waiting",
                "message": "浏览器已打开，请使用抖音APP扫码登录。登录完成后请点击确认登录按钮。",
            }
        except Exception as e:
            await self.stop()
            return {
                "status": "error",
                "message": f"打开浏览器失败: {str(e)}",
            }

    async def confirm_login(self) -> dict:
        if not self.context:
            return {"status": "error", "message": "浏览器未启动，请先点击扫码登录"}

        try:
            await self.save_cookies()
            self._login_mode = False
            await self.stop()
            return {"status": "success", "message": "登录态已保存"}
        except Exception as e:
            return {"status": "error", "message": f"保存登录态失败: {str(e)}"}

    async def scrape_favorites(
        self,
        max_count: Optional[int] = None,
        on_progress: Optional[Callable] = None,
    ) -> list[dict]:
        if not self.page:
            success = await self.start(headless=True)
            if not success:
                raise Exception("启动浏览器失败")

        page = self.page

        try:
            await page.goto("https://www.douyin.com", wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(3)

            is_logged_in = await self.check_login_status()
            if not is_logged_in:
                raise Exception("未登录，请先扫码登录")

            user_link = await page.query_selector('[data-e2e="user-info"]')
            if user_link:
                href = await user_link.get_attribute("href")
                if href:
                    user_url = f"https://www.douyin.com{href}" if href.startswith("/") else href
                    await page.goto(user_url, wait_until="domcontentloaded", timeout=30000)
                    await asyncio.sleep(2)

            fav_tab = await page.query_selector('[data-e2e="user-tab-favorite"]')
            if fav_tab:
                await fav_tab.click()
                await asyncio.sleep(2)

            videos = []
            seen_urls = set()
            no_new_count = 0

            while True:
                if max_count and len(videos) >= max_count:
                    break

                items = await page.query_selector_all('[data-e2e="user-post-list"] > div')

                if not items:
                    items = await page.query_selector_all('div[class*="ECMy_UnAe"] > div')

                if not items:
                    items = await page.query_selector_all('ul li div[class*="Item"]')

                new_this_round = 0
                for item in items:
                    try:
                        link = await item.query_selector("a")
                        if not link:
                            continue

                        href = await link.get_attribute("href")
                        if not href:
                            continue

                        url = href if href.startswith("http") else f"https://www.douyin.com{href}"

                        if url in seen_urls:
                            continue

                        seen_urls.add(url)

                        title_el = await item.query_selector('[class*="title"]') or await item.query_selector("a span")
                        title = await title_el.inner_text() if title_el else ""

                        author_el = await item.query_selector('[class*="author"]') or await item.query_selector('[class*="nickname"]')
                        author = await author_el.inner_text() if author_el else ""

                        desc_el = await item.query_selector('[class*="desc"]')
                        desc = await desc_el.inner_text() if desc_el else ""

                        cover_el = await item.query_selector("img")
                        cover_url = await cover_el.get_attribute("src") if cover_el else ""

                        video_data = {
                            "url": url,
                            "title": title.strip(),
                            "author": author.strip(),
                            "author_id": "",
                            "desc": desc.strip(),
                            "cover_url": cover_url,
                        }

                        videos.append(video_data)
                        new_this_round += 1

                        if on_progress:
                            await on_progress({
                                "type": "found",
                                "total": len(videos),
                                "current": video_data,
                            })

                        if max_count and len(videos) >= max_count:
                            break

                    except Exception as e:
                        continue

                if new_this_round == 0:
                    no_new_count += 1
                    if no_new_count >= 3:
                        break
                else:
                    no_new_count = 0

                scroll_distance = random.randint(600, 1000)
                await page.evaluate(f"window.scrollBy(0, {scroll_distance})")
                await asyncio.sleep(random.uniform(1.5, 3.0))

            return videos

        except Exception as e:
            raise Exception(f"抓取失败: {str(e)}")

    async def save_cookies(self):
        if self.context:
            try:
                cookies = await self.context.cookies()
                auth_manager.save_cookies(cookies)
            except Exception:
                pass


scraper = DouyinScraper()
