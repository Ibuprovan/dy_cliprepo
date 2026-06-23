# backend/app/scraper/auth_manager.py
"""
抖音登录态管理模块
功能：登录、验证、加载登录态
核心原则：只保存storage_state（cookies + localStorage），禁止只保存cookies
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional

from playwright.async_api import async_playwright, Browser, BrowserContext, Page

from app.core.config import (
    AUTH_FILE,
    DATA_DIR,
    DOUYIN_HOME_URL,
    DOUYIN_USER_URL,
    BROWSER_ARGS,
    USER_AGENT,
    STEALTH_JS,
)

# 配置日志
logger = logging.getLogger(__name__)


class AuthError(Exception):
    """登录态相关错误"""
    pass


class AuthFileNotFoundError(AuthError):
    """登录态文件不存在"""
    pass


async def run_login_flow() -> Path:
    """
    人工扫码登录流程
    1. 打开有头浏览器
    2. 访问抖音首页
    3. 等待用户扫码登录
    4. 保存storage_state到文件
    
    Returns:
        Path: 登录态文件路径
    
    Raises:
        AuthError: 登录失败
    """
    # 确保data目录存在
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    async with async_playwright() as p:
        # 启动有头浏览器（用户需要看到界面扫码）
        # 为什么用headless=False：用户需要手动扫码
        browser = await p.chromium.launch(
            headless=False,
            args=BROWSER_ARGS,
        )
        
        # 创建浏览器上下文
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent=USER_AGENT,
            locale="zh-CN",
        )
        
        # 创建页面
        page = await context.new_page()
        
        # 注入反检测脚本
        # 为什么需要：navigator.webdriver=true是自动化工具的典型特征
        await page.add_init_script(STEALTH_JS)
        
        try:
            # 访问抖音首页
            print("\n正在打开抖音...")
            await page.goto(DOUYIN_HOME_URL)
            await page.wait_for_load_state("domcontentloaded")
            await asyncio.sleep(3)
            
            # 提示用户扫码
            print("\n" + "=" * 60)
            print("  请在弹出的浏览器中完成抖音扫码登录")
            print("")
            print("  登录成功的标志：")
            print("    - 页面右上角出现你的头像")
            print("    - 或页面显示「我的主页」「退出登录」等字样")
            print("")
            print("  登录成功后，在此窗口按回车键保存登录态...")
            print("=" * 60 + "\n")
            
            # 等待用户按回车
            await asyncio.get_event_loop().run_in_executor(None, input)
            
            # 等待页面稳定
            await asyncio.sleep(2)
            
            # 验证登录状态
            is_logged_in = await _verify_login_state(page)
            
            if is_logged_in:
                print("\n✓ 检测到登录成功！")
            else:
                print("\n⚠ 未检测到登录状态")
                choice = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: input("如果你确认已登录，请输入 y 仍然保存 (y/N): ").strip().lower()
                )
                if choice != 'y':
                    print("已取消保存")
                    raise AuthError("用户取消保存")
            
            # 保存storage_state
            # 为什么用storage_state而不是只保存cookies：
            # storage_state包含cookies + localStorage，抖音的登录态可能存储在localStorage中
            await context.storage_state(path=str(AUTH_FILE))
            
            file_size = AUTH_FILE.stat().st_size
            print(f"\n✓ 登录态已保存到 {AUTH_FILE}")
            print(f"  文件大小: {file_size} bytes")
            
            return AUTH_FILE
            
        except AuthError:
            raise
        except Exception as e:
            raise AuthError(f"登录流程失败: {e}")
        finally:
            await browser.close()


async def _verify_login_state(page: Page) -> bool:
    """
    验证页面登录状态
    通过检查页面内容判断是否已登录
    """
    try:
        # 检查页面是否有用户相关元素
        content = await page.content()
        
        # 登录成功的标志
        login_indicators = ["我的主页", "个人主页", "退出登录", "我的收藏", "关注", "粉丝"]
        for indicator in login_indicators:
            if indicator in content:
                return True
        
        # 检查URL是否在个人页面
        if "/user/" in page.url and "login" not in page.url:
            return True
        
        return False
    except Exception:
        return False


async def load_auth_context(browser: Browser) -> BrowserContext:
    """
    加载已保存的登录态到浏览器上下文
    供同步模块使用
    
    Args:
        browser: Playwright浏览器实例
    
    Returns:
        BrowserContext: 包含登录态的浏览器上下文
    
    Raises:
        AuthFileNotFoundError: 登录态文件不存在
        AuthError: 登录态加载失败
    """
    # 检查登录态文件是否存在
    if not AUTH_FILE.exists():
        raise AuthFileNotFoundError(
            f"登录态文件不存在: {AUTH_FILE}\n"
            "请先运行 login_manual.py 完成登录"
        )
    
    try:
        # 创建浏览器上下文并加载storage_state
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=USER_AGENT,
            locale="zh-CN",
            storage_state=str(AUTH_FILE),
        )

        # 注入反检测脚本到上下文级别（所有页面都会生效）
        await context.add_init_script(STEALTH_JS)

        return context

    except Exception as e:
        raise AuthError(f"加载登录态失败: {e}")


def get_auth_file_path() -> Path:
    """获取登录态文件路径"""
    return AUTH_FILE


def is_auth_exists() -> bool:
    """检查登录态文件是否存在"""
    return AUTH_FILE.exists()
