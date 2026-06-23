# backend/test_eventloop.py
"""
测试事件循环策略
"""

import sys
import asyncio

# 设置策略
if sys.platform == "win32":
    print(f"[1] 设置前: {asyncio.get_event_loop_policy()}")
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    print(f"[2] 设置后: {asyncio.get_event_loop_policy()}")

async def test():
    print(f"[3] 运行中: {asyncio.get_event_loop()}")
    print(f"[4] 类型: {type(asyncio.get_event_loop())}")
    
    # 测试子进程
    try:
        proc = await asyncio.create_subprocess_exec(
            "python", "--version",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        print(f"[5] 子进程成功: {stdout.decode().strip()}")
    except NotImplementedError as e:
        print(f"[5] 子进程失败: NotImplementedError: {e}")
    except Exception as e:
        print(f"[5] 子进程失败: {type(e).__name__}: {e}")

if __name__ == "__main__":
    print(f"[0] 平台: {sys.platform}")
    asyncio.run(test())
