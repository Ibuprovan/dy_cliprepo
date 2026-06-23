# backend/login_manual.py
"""
抖音手动登录脚本
功能：打开浏览器让用户扫码登录，保存登录态
运行方式：cd backend && python login_manual.py
与同步逻辑完全解耦，可独立运行
"""

import sys
import asyncio
from pathlib import Path

# 确保可以导入app模块
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.scraper.auth_manager import run_login_flow, AuthError


async def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("  抖音收藏AI知识库 - 手动登录")
    print("=" * 60)
    print("\n此脚本将打开浏览器，让你扫码登录抖音。")
    print("登录成功后，登录态将保存到 data/douyin_auth.json\n")
    
    try:
        auth_file = await run_login_flow()
        
        print("\n" + "=" * 60)
        print("  登录完成！")
        print("=" * 60)
        print(f"\n登录态已保存到: {auth_file}")
        print("\n下一步：")
        print("  1. 运行 start.bat 启动服务")
        print("  2. 或运行 python test_sync.py 测试同步功能")
        
        return 0
        
    except AuthError as e:
        print(f"\n[X] 登录失败: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n\n用户取消操作")
        return 1
    except Exception as e:
        print(f"\n[X] 未知错误: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
