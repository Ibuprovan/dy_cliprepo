# backend/test_sync.py
"""
同步功能测试脚本
运行方式：cd backend && python test_sync.py
测试是否能成功拉取1条视频数据
"""

import sys
import asyncio
from pathlib import Path

# 确保可以导入app模块
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.scraper.auth_manager import AuthFileNotFoundError, AuthError
from app.scraper.sync_engine import fetch_favorites_list, SyncError
from app.core.config import AUTH_FILE


async def test_sync():
    """测试同步功能"""
    print("\n" + "=" * 60)
    print("  抖音收藏AI知识库 - 同步测试")
    print("=" * 60)
    
    # 检查登录态文件
    print(f"\n[1/3] 检查登录态文件...")
    if not AUTH_FILE.exists():
        print(f"[FAIL] 登录态文件不存在: {AUTH_FILE}")
        print("  请先运行: python login_manual.py")
        return 1
    
    file_size = AUTH_FILE.stat().st_size
    print(f"[OK] 登录态文件存在 ({file_size} bytes)")
    
    # 测试拉取
    print(f"\n[2/3] 开始拉取收藏（限制1条）...")
    print("  这可能需要30秒左右，请耐心等待...\n")
    
    try:
        videos = await fetch_favorites_list(limit=1)
        
        print(f"\n[3/3] 测试结果...")
        if videos:
            for i, video in enumerate(videos):
                print(f"  [OK] 成功获取视频 #{i+1}:")
                print(f"    标题: {video['title']}")
                print(f"    作者: {video['author']}")
                print(f"    URL:  {video['url']}")
                desc = video['desc'][:50] + "..." if len(video['desc']) > 50 else video['desc']
                print(f"    描述: {desc}")
            
            print(f"\n[OK] 测试成功！成功拉取 {len(videos)} 条视频")
            print("\n下一步：")
            print("  1. 运行 start.bat 启动完整服务")
            print("  2. 访问 http://localhost:5173 查看前端界面")
            return 0
        else:
            print("[FAIL] 测试失败：未能获取任何视频")
            print("  可能原因：收藏列表为空，或页面结构变化")
            return 1
            
    except AuthFileNotFoundError as e:
        print(f"[FAIL] 登录态文件不存在: {e}")
        print("  修复：python login_manual.py")
        return 1
    except AuthError as e:
        print(f"[FAIL] 登录态错误: {e}")
        print("  修复：python login_manual.py 重新登录")
        return 1
    except SyncError as e:
        print(f"[FAIL] 同步错误: {e}")
        print("  检查日志: data/logs/sync.log")
        return 1
    except Exception as e:
        print(f"[FAIL] 未知错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        print("  检查日志: data/logs/sync.log")
        return 1


def main():
    """主函数"""
    try:
        return asyncio.run(test_sync())
    except KeyboardInterrupt:
        print("\n\n用户取消操作")
        return 1


if __name__ == "__main__":
    sys.exit(main())
