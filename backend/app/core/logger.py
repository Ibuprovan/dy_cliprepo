import logging
import threading
from collections import deque
from datetime import datetime
from typing import List, Dict

_lock = threading.Lock()
_buffer: deque = deque(maxlen=500)


class RingBufferHandler(logging.Handler):
    """环形缓冲区日志处理器，保留最近 N 条日志供调试 API 查询"""

    def __init__(self, maxlen: int = 500):
        super().__init__()
        self.maxlen = maxlen
        self._buf = deque(maxlen=maxlen)

    def emit(self, record: logging.LogRecord):
        entry = {
            "time": datetime.fromtimestamp(record.created).isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "ai_input"):
            entry["ai_input"] = record.ai_input
        if hasattr(record, "ai_output"):
            entry["ai_output"] = record.ai_output
        with _lock:
            self._buf.append(entry)

    def get_recent(self, n: int = 100, min_level: str = "DEBUG") -> List[Dict]:
        levels = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3, "CRITICAL": 4}
        min_lv = levels.get(min_level.upper(), 0)
        with _lock:
            result = [e for e in self._buf if levels.get(e["level"], 0) >= min_lv]
            return result[-n:]


_handler: RingBufferHandler = None


def setup_debug_logging():
    global _handler
    if _handler is not None:
        return
    _handler = RingBufferHandler(maxlen=500)
    _handler.setLevel(logging.DEBUG)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s - %(message)s")
    _handler.setFormatter(fmt)
    root = logging.getLogger()
    root.addHandler(_handler)
    root.setLevel(logging.DEBUG)


def get_recent_logs(n: int = 100, min_level: str = "DEBUG") -> List[Dict]:
    if _handler is None:
        return []
    return _handler.get_recent(n, min_level)
