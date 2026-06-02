import asyncio
import os
from typing import Callable, Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

from app.config import settings
from app.scraper.auth_manager import auth_manager


class DouyinScraper:
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    async def start(self, headless: bool = True):
        self._playwright = await async_playwright().start()
        self.browser = await self._playwright.chromium.launch(headless=headless)
        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )

        cookies = auth_manager.load_cookies()
        if cookies:
            await self.context.add_cookies(cookies)

        self.page = await self.context.new_page()

    async def stop(self):
        if self.browser:
            await self.browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def scrape_favorites(
        self,
        max_count: Optional[int] = None,
        on_progress: Optional[Callable] = None,
    ) -> list[dict]:
        if not self.page:
            await self.start(headless=False)

        page = self.page

        await page.goto("https://www.douyin.com", wait_until="networkidle")
        await asyncio.sleep(2)

        user_link = await page.query_selector('[data-e2e="user-info"]')
        if user_link:
            href = await user_link.get_attribute("href")
            if href:
                user_url = f"https://www.douyin.com{href}" if href.startswith("/") else href
                await page.goto(user_url, wait_until="networkidle")
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

            await page.evaluate("window.scrollBy(0, 800)")
            await asyncio.sleep(2)

        return videos

    async def save_cookies(self):
        if self.context:
            cookies = await self.context.cookies()
            auth_manager.save_cookies(cookies)


scraper = DouyinScraper()
