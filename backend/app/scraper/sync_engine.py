# backend/app/scraper/sync_engine.py
"""
抖音收藏同步引擎
功能：无头浏览器拉取收藏列表
核心原则：只读、无头、容错
"""

import asyncio
import logging
import random
import sys
from datetime import datetime
from pathlib import Path
from typing import AsyncGenerator, Dict, List, Optional, Set

from playwright.async_api import async_playwright, Browser, BrowserContext, Page

from app.core.config import (
    AUTH_FILE,
    LOGS_DIR,
    DOUYIN_HOME_URL,
    BROWSER_ARGS,
    USER_AGENT,
    STEALTH_JS,
    SCROLL_WAIT_MIN,
    SCROLL_WAIT_MAX,
    VIDEO_PAGE_TIMEOUT,
    VIDEO_PAGE_RENDER_WAIT,
)
from app.scraper.auth_manager import (
    AuthFileNotFoundError,
    AuthError,
    load_auth_context,
)
from app.scraper.selectors import (
    VIDEO_LIST_SELECTORS,
    VIDEO_LINK_SELECTORS,
    VIDEO_TITLE_SELECTORS,
    VIDEO_DESC_SELECTORS,
    VIDEO_COVER_SELECTORS,
    FAVORITE_TAB_SELECTORS,
    VIDEO_DESC_DETAIL_SELECTORS,
    VIDEO_SOURCE_SELECTORS,
    VIDEO_PAGE_ERROR_KEYWORDS,
    VIDEO_PAGE_NOISE_KEYWORDS,
)

# 配置日志
logger = logging.getLogger(__name__)


class SyncError(Exception):
    """同步相关错误"""
    pass


def setup_sync_logger():
    """
    设置同步专用日志器
    为什么单独设置：同步日志需要写入文件，便于排查问题
    应在应用启动时调用，而非模块导入时
    """
    if logger.handlers:
        return  # 已经设置过，避免重复添加

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOGS_DIR / "sync.log"

    # 创建文件处理器
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    )

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    )

    # 添加到logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.setLevel(logging.DEBUG)


async def _extract_video_info(item) -> Optional[Dict]:
    """
    从页面元素提取视频信息
    为什么用多个选择器：抖音页面结构可能变化，需要容错
    
    抖音收藏页面结构分析（2026-06-03）：
    - 链接：<a href="/video/xxx">
    - 标题：在img的alt属性中，或在p标签中
    - 描述：在p标签中
    """
    try:
        # 获取链接
        link = None
        for selector in VIDEO_LINK_SELECTORS:
            link = await item.query_selector(selector)
            if link:
                break
        
        if not link:
            return None
        
        href = await link.get_attribute("href")
        if not href:
            return None
        
        # 构建完整URL
        url = href if href.startswith("http") else f"https://www.douyin.com{href}"
        
        # 获取标题（优先从img的alt属性获取）
        title = ""
        for selector in VIDEO_TITLE_SELECTORS:
            title_el = await item.query_selector(selector)
            if title_el:
                if selector == 'img[alt]':
                    alt_value = await title_el.get_attribute("alt")
                    title = alt_value or ""
                else:
                    title = await title_el.inner_text()
                if title.strip():
                    break
        
        # 获取作者（抖音收藏页面可能不显示作者，留空）
        author = ""
        
        # 获取封面图片
        cover_url = ""
        for selector in VIDEO_COVER_SELECTORS:
            cover_el = await item.query_selector(selector)
            if cover_el:
                src = await cover_el.get_attribute("data-src") or await cover_el.get_attribute("src")
                if src:
                    cover_url = src.strip()
                    break
        
        # 获取描述（从p标签获取）
        desc = ""
        for selector in VIDEO_DESC_SELECTORS:
            desc_el = await item.query_selector(selector)
            if desc_el:
                desc = await desc_el.inner_text()
                if desc.strip():
                    break
        
        # 如果标题为空，尝试从描述获取
        if not title.strip() and desc.strip():
            title = desc[:50]
        
        return {
            "url": url,
            "title": title.strip(),
            "author": author.strip(),
            "desc": desc.strip(),
            "cover_url": cover_url,
            "scraped_at": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.warning(f"提取视频信息失败: {e}")
        return None


import re as _re

# 播放器时间显示正则（如 00:00 / 00:00, 1:23:45 / 10:00）
_PLAYER_TIME_RE = _re.compile(r'\d{1,2}:\d{2}(?::\d{2})?\s*/\s*\d{1,2}:\d{2}(?::\d{2})?')


def _is_noise_text(text: str) -> bool:
    """检查文本是否是无意义的播放器 UI/导航/错误文本"""
    text = text.strip()
    if len(text) < 15:
        return True
    for kw in VIDEO_PAGE_ERROR_KEYWORDS:
        if kw in text:
            return True
    # 播放器控制条文本特征：倍速/清屏/连播/章节要点同时出现
    player_hits = sum(1 for kw in VIDEO_PAGE_NOISE_KEYWORDS if kw in text)
    if player_hits >= 2:
        return True
    # 播放器时间显示（00:00 / 00:00 开头）是典型播放器 UI
    if _PLAYER_TIME_RE.search(text):
        return True
    return False


async def extract_video_page_info(page: Page, url: str) -> Dict:
    """
    打开视频详情页，提取完整描述和视频源地址
    包含错误检测和内容校验，避免将错误页面/导航文本送入 AI
    """
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=VIDEO_PAGE_TIMEOUT)
        await asyncio.sleep(VIDEO_PAGE_RENDER_WAIT)

        # 检查页面是否跳转到非正常地址（登录页/首页等）
        current_url = page.url
        if "login" in current_url or "/error" in current_url:
            logger.warning(f"视频页跳转到非正常页面: {current_url}")
            return {"desc": "", "video_src_url": ""}

        # 提取描述（过滤无意义内容）
        full_desc = ""
        for selector in VIDEO_DESC_DETAIL_SELECTORS:
            els = await page.query_selector_all(selector)
            for el in els:
                text = (await el.inner_text()).strip()
                if text and not _is_noise_text(text):
                    full_desc = text
                    break
            if full_desc:
                break

        # 提取视频源地址
        video_src_url = ""
        for selector in VIDEO_SOURCE_SELECTORS:
            el = await page.query_selector(selector)
            if el:
                url = await el.get_attribute("src")
                if url:
                    video_src_url = url.strip()
                    break

        logger.info(
            f"详情页提取: desc_len={len(full_desc)} "
            f"video_url={'yes' if video_src_url else 'no'} | {url}"
        )
        return {"desc": full_desc, "video_src_url": video_src_url}

    except Exception as e:
        logger.warning(f"提取视频详情页信息失败 {url}: {e}")
        return {"desc": "", "video_src_url": ""}


async def _navigate_to_favorites(page: Page) -> bool:
    """
    导航到收藏页面
    为什么先访问个人主页再点击收藏：直接访问收藏URL可能需要登录态验证
    """
    try:
        # 访问个人主页
        logger.info("正在访问个人主页...")
        await page.goto("https://www.douyin.com/user/self", wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)
        
        # 检查是否跳转到登录页
        if "login" in page.url:
            logger.error("登录态已失效，跳转到登录页")
            return False
        
        # 点击收藏标签
        for selector in FAVORITE_TAB_SELECTORS:
            try:
                element = await page.query_selector(selector)
                if element:
                    await element.click()
                    await asyncio.sleep(2)
                    logger.info("成功进入收藏页面")
                    return True
            except Exception:
                continue
        
        logger.error("无法找到收藏标签")
        return False
        
    except Exception as e:
        logger.error(f"导航到收藏页面失败: {e}")
        return False


async def fetch_favorites(
    limit: int = 10,
    existing_urls: Optional[Set[str]] = None,
) -> AsyncGenerator[Dict, None]:
    """
    拉取收藏视频列表（异步生成器）
    
    Args:
        limit: 最大拉取数量
        existing_urls: 已存在的URL集合（用于去重）
    
    Yields:
        Dict: 视频信息字典，包含 url, title, author, desc, scraped_at
    
    Raises:
        AuthFileNotFoundError: 登录态文件不存在
        AuthError: 登录态加载失败
        SyncError: 同步过程错误
    """
    if existing_urls is None:
        existing_urls = set()
    
    logger.info(f"开始拉取收藏，限制数量: {limit}")
    
    # 检查登录态文件
    if not AUTH_FILE.exists():
        raise AuthFileNotFoundError(
            f"登录态文件不存在: {AUTH_FILE}\n"
            "请先运行 login_manual.py 完成登录"
        )
    
    async with async_playwright() as p:
        browser = None
        try:
            # 启动无头浏览器
            # 为什么用headless=True：同步过程不需要用户界面
            browser = await p.chromium.launch(
                headless=True,
                args=BROWSER_ARGS,
            )
            
            # 加载登录态
            context = await load_auth_context(browser)
            page = await context.new_page()
            
            # 导航到收藏页面
            if not await _navigate_to_favorites(page):
                raise SyncError("无法进入收藏页面，登录态可能已失效")
            
            # 开始滚动加载
            seen_urls = set(existing_urls)
            found_count = 0
            no_new_count = 0
            
            while found_count < limit:
                # 等待页面加载完成
                await asyncio.sleep(2)
                
                # 获取当前页面的视频元素
                items = []
                for selector in VIDEO_LIST_SELECTORS:
                    items = await page.query_selector_all(selector)
                    if items:
                        break
                
                new_this_round = 0
                
                for item in items:
                    if found_count >= limit:
                        break
                    
                    video_info = await _extract_video_info(item)
                    
                    if not video_info:
                        continue
                    
                    url = video_info["url"]
                    
                    # 跳过已存在的
                    if url in seen_urls:
                        continue
                    
                    seen_urls.add(url)
                    found_count += 1
                    new_this_round += 1
                    
                    logger.info(f"找到视频 [{found_count}/{limit}]: {video_info['title']}")
                    
                    # yield视频信息
                    yield video_info
                
                # 检查是否没有新视频
                if new_this_round == 0:
                    no_new_count += 1
                    if no_new_count >= 3:
                        logger.info("连续3次没有新视频，停止滚动")
                        break
                else:
                    no_new_count = 0
                
                # 随机滚动，模拟人类行为
                # 为什么随机：避免被检测为自动化工具
                scroll_distance = random.randint(600, 1000)
                await page.evaluate(f"window.scrollBy(0, {scroll_distance})")
                
                # 随机等待
                wait_time = random.uniform(SCROLL_WAIT_MIN, SCROLL_WAIT_MAX)
                await asyncio.sleep(wait_time)
            
            logger.info(f"拉取完成，共找到 {found_count} 个视频")
            
        except (AuthFileNotFoundError, AuthError):
            raise
        except Exception as e:
            logger.error(f"同步过程出错: {e}", exc_info=True)
            raise SyncError(f"同步失败: {e}")
        finally:
            if browser:
                await browser.close()


async def fetch_favorites_list(
    limit: int = 10,
    existing_urls: Optional[Set[str]] = None,
) -> List[Dict]:
    """
    拉取收藏视频列表（返回完整列表）
    为什么需要这个函数：某些场景需要一次性获取所有结果
    
    Args:
        limit: 最大拉取数量
        existing_urls: 已存在的URL集合
    
    Returns:
        List[Dict]: 视频信息列表
    """
    videos = []
    async for video in fetch_favorites(limit, existing_urls):
        videos.append(video)
    return videos


async def fetch_favorites_enriched(
    limit: int = 10,
    existing_urls: Optional[Set[str]] = None,
) -> List[Dict]:
    """
    增强版同步：拉取收藏列表 + 对每个新视频打开详情页获取完整描述和视频源

    适用场景：AI 总结需要更丰富的视频内容（完整 desc 或视频源 URL）。
    为什么不在 fetch_favorites 里直接做：保持向后兼容，不改变基础拉取行为。
    """
    if existing_urls is None:
        existing_urls = set()

    logger.info(f"开始增强同步（含详情页），数量限制: {limit}")

    if not AUTH_FILE.exists():
        raise AuthFileNotFoundError(
            f"登录态文件不存在: {AUTH_FILE}\n"
            "请先运行 login_manual.py 完成登录"
        )

    async with async_playwright() as p:
        browser = None
        try:
            browser = await p.chromium.launch(
                headless=True,
                args=BROWSER_ARGS,
            )

            context = await load_auth_context(browser)
            page = await context.new_page()

            if not await _navigate_to_favorites(page):
                raise SyncError("无法进入收藏页面，登录态可能已失效")

            seen_urls = set(existing_urls)
            found_count = 0
            no_new_count = 0
            enriched = []

            while found_count < limit:
                await asyncio.sleep(2)

                items = []
                for selector in VIDEO_LIST_SELECTORS:
                    items = await page.query_selector_all(selector)
                    if items:
                        break

                new_this_round = 0

                for item in items:
                    if found_count >= limit:
                        break

                    video_info = await _extract_video_info(item)
                    if not video_info:
                        continue

                    url = video_info["url"]
                    if url in seen_urls:
                        continue

                    seen_urls.add(url)
                    found_count += 1
                    new_this_round += 1

                    # 打开详情页获取完整描述和视频源
                    # 单个详情页失败不应中止整条同步
                    try:
                        detail_page = await context.new_page()
                        try:
                            extra = await extract_video_page_info(detail_page, url)
                            if extra["desc"]:
                                video_info["desc"] = extra["desc"]
                            video_info["video_src_url"] = extra["video_src_url"]
                        finally:
                            await detail_page.close()
                    except Exception as e:
                        logger.warning(f"详情页抓取失败，跳过增强: {url} | {e}")
                        video_info["video_src_url"] = ""

                    logger.info(
                        f"视频 [{found_count}/{limit}]: {video_info['title']} "
                        f"| desc_len={len(video_info['desc'])} "
                        f"| has_video={'yes' if video_info['video_src_url'] else 'no'}"
                    )
                    enriched.append(video_info)

                if new_this_round == 0:
                    no_new_count += 1
                    if no_new_count >= 3:
                        logger.info("连续3次没有新视频，停止滚动")
                        break
                else:
                    no_new_count = 0

                scroll_distance = random.randint(600, 1000)
                await page.evaluate(f"window.scrollBy(0, {scroll_distance})")
                wait_time = random.uniform(SCROLL_WAIT_MIN, SCROLL_WAIT_MAX)
                await asyncio.sleep(wait_time)

            logger.info(f"增强同步完成，共 {len(enriched)} 个视频")
            return enriched

        except (AuthFileNotFoundError, AuthError):
            raise
        except Exception as e:
            logger.error(f"增强同步过程出错: {e}", exc_info=True)
            raise SyncError(f"同步失败: {e}")
        finally:
            if browser:
                await browser.close()
