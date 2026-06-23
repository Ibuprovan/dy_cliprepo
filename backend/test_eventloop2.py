# backend/test_eventloop2.py
"""
测试事件循环策略 - ProactorEventLoop
"""

import sys
import asyncio

async def test():
    print(f"[1] 事件循环: {type(asyncio.get_event_loop())}")
    
    # 测试子进程
    try:
        proc = await asyncio.create_subprocess_exec(
            "python", "--version",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        print(f"[2] 子进程成功: {stdout.decode().strip()}")
    except NotImplementedError as e:
        print(f"[2] 子进程失败: NotImplementedError: {e}")
    except Exception as e:
        print(f"[2] 子进程失败: {type(e).__name__}: {e}")

if __name__ == "__main__":
    print(f"[0] 平台: {sys.platform}")
    # 不设置策略，使用默认的ProactorEventLoop
    asyncio.run(test())
