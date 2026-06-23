#!/usr/bin/env python3
"""
端到端测试脚本
使用 Playwright 进行浏览器自动化测试
"""

import asyncio
import sys
import time
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from playwright.async_api import async_playwright


class E2ETestResult:
    """测试结果记录"""
    def __init__(self):
        self.passed = []
        self.failed = []
        self.errors = []
    
    def add_pass(self, test_name: str, detail: str = ""):
        self.passed.append({"name": test_name, "detail": detail})
        print(f"  [PASS] {test_name}")
    
    def add_fail(self, test_name: str, detail: str = ""):
        self.failed.append({"name": test_name, "detail": detail})
        print(f"  [FAIL] {test_name}: {detail}")
    
    def add_error(self, test_name: str, error: str):
        self.errors.append({"name": test_name, "error": error})
        print(f"  [ERROR] {test_name}: ERROR - {error}")
    
    def summary(self):
        print("\n" + "=" * 60)
        print("  测试结果汇总")
        print("=" * 60)
        print(f"  通过: {len(self.passed)}")
        print(f"  失败: {len(self.failed)}")
        print(f"  错误: {len(self.errors)}")
        print()
        
        if self.failed:
            print("  失败项:")
            for item in self.failed:
                print(f"    - {item['name']}: {item['detail']}")
        
        if self.errors:
            print("  错误项:")
            for item in self.errors:
                print(f"    - {item['name']}: {item['error']}")
        
        print()
        return len(self.failed) == 0 and len(self.errors) == 0


async def run_e2e_tests():
    """运行端到端测试"""
    result = E2ETestResult()
    
    print("\n" + "=" * 60)
    print("  端到端测试")
    print("=" * 60)
    print()
    
    async with async_playwright() as p:
        # 启动浏览器
        print("[1/6] 启动浏览器...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # 收集控制台错误
        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        
        # 收集页面错误
        page_errors = []
        page.on("pageerror", lambda error: page_errors.append(str(error)))
        
        try:
            # 测试 1: 前端页面加载
            print("\n[2/6] 测试前端页面加载...")
            try:
                await page.goto("http://localhost:5173", timeout=10000)
                await page.wait_for_load_state("networkidle", timeout=10000)
                result.add_pass("前端页面加载")
            except Exception as e:
                result.add_error("前端页面加载", str(e))
                # 如果前端无法加载，后续测试可能无法进行
                await browser.close()
                result.summary()
                return result
            
            # 测试 2: 后端健康检查
            print("\n[3/6] 测试后端健康检查...")
            try:
                response = await page.evaluate("""
                    async () => {
                        const res = await fetch('/health');
                        return await res.json();
                    }
                """)
                if response.get("status") == "ok":
                    result.add_pass("后端健康检查", f"auth_exists={response.get('auth_exists')}")
                else:
                    result.add_fail("后端健康检查", f"状态异常: {response}")
            except Exception as e:
                result.add_error("后端健康检查", str(e))
            
            # 测试 3: 页面元素检查
            print("\n[4/6] 测试页面元素...")
            
            # 检查标题
            try:
                title = await page.title()
                if title:
                    result.add_pass("页面标题", title)
                else:
                    result.add_fail("页面标题", "标题为空")
            except Exception as e:
                result.add_error("页面标题", str(e))
            
            # 检查主要元素
            selectors = {
                "h1 标题": "h1",
                "同步按钮": "button",
            }
            
            for name, selector in selectors.items():
                try:
                    element = await page.query_selector(selector)
                    if element:
                        result.add_pass(f"页面元素: {name}")
                    else:
                        result.add_fail(f"页面元素: {name}", f"未找到 {selector}")
                except Exception as e:
                    result.add_error(f"页面元素: {name}", str(e))
            
            # 检查视频列表区域（可能是空状态或表格）
            try:
                # 检查是否有视频表格或空状态提示
                video_area = await page.query_selector("table, [class*='video'], [class*='list'], div:has-text('暂无视频')")
                if video_area:
                    result.add_pass("页面元素: 视频列表区域")
                else:
                    result.add_fail("页面元素: 视频列表区域", "未找到视频列表相关元素")
            except Exception as e:
                result.add_error("页面元素: 视频列表区域", str(e))
            
            # 测试 4: API 端点
            print("\n[5/6] 测试 API 端点...")
            
            api_tests = [
                ("GET /health", "/health"),
                ("GET /api/videos", "/api/videos"),
            ]
            
            for name, endpoint in api_tests:
                try:
                    response = await page.evaluate(f"""
                        async () => {{
                            const res = await fetch('{endpoint}');
                            return {{ status: res.status, ok: res.ok }};
                        }}
                    """)
                    if response.get("ok"):
                        result.add_pass(f"API: {name}")
                    else:
                        result.add_fail(f"API: {name}", f"HTTP {response.get('status')}")
                except Exception as e:
                    result.add_error(f"API: {name}", str(e))
            
            # 测试 5: 同步按钮交互
            print("\n[6/6] 测试同步按钮交互...")
            try:
                # 查找同步按钮
                sync_button = await page.query_selector("button:has-text('同步'), button:has-text('开始')")
                if sync_button:
                    # 检查按钮是否可点击
                    is_disabled = await sync_button.get_attribute("disabled")
                    if is_disabled:
                        result.add_pass("同步按钮状态", "按钮存在但被禁用（可能需要登录）")
                    else:
                        result.add_pass("同步按钮状态", "按钮可点击")
                else:
                    result.add_fail("同步按钮", "未找到同步按钮")
            except Exception as e:
                result.add_error("同步按钮", str(e))
            
            # 检查控制台错误
            if console_errors:
                print(f"\n  ⚠️ 发现 {len(console_errors)} 个控制台错误:")
                for err in console_errors[:5]:  # 只显示前 5 个
                    print(f"    - {err[:100]}")
            
            if page_errors:
                print(f"\n  ⚠️ 发现 {len(page_errors)} 个页面错误:")
                for err in page_errors[:5]:
                    print(f"    - {err[:100]}")
            
        except Exception as e:
            result.add_error("测试执行", str(e))
        
        finally:
            await browser.close()
    
    # 输出汇总
    success = result.summary()
    
    # 保存错误日志
    if console_errors or page_errors:
        log_file = Path(__file__).parent.parent / "data" / "logs" / "e2e_errors.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(log_file, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("端到端测试错误日志\n")
            f.write("=" * 60 + "\n\n")
            
            if console_errors:
                f.write("控制台错误:\n")
                for err in console_errors:
                    f.write(f"  - {err}\n")
                f.write("\n")
            
            if page_errors:
                f.write("页面错误:\n")
                for err in page_errors:
                    f.write(f"  - {err}\n")
        
        print(f"\n  错误日志已保存到: {log_file}")
    
    return result


if __name__ == "__main__":
    result = asyncio.run(run_e2e_tests())
    sys.exit(0 if result.failed == [] and result.errors == [] else 1)
