# backend/app/core/config.py
"""
统一配置模块
所有路径基于项目根目录，禁止硬编码绝对路径
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# 项目根目录：backend/app/core/config.py -> backend/app/core -> backend/app -> backend -> 项目根目录
# 为什么这样写：确保无论从哪里运行脚本，路径都是相对于项目根目录的
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# 加载 .env 文件
load_dotenv(BASE_DIR / "backend" / ".env")

# ==================== 目录路径 ====================
# 后端目录
BACKEND_DIR = BASE_DIR / "backend"

# 后端源码目录
BACKEND_SRC = BACKEND_DIR / "app"

# 数据目录：所有运行时数据存储位置
DATA_DIR = BACKEND_DIR / "data"

# 日志目录
LOGS_DIR = DATA_DIR / "logs"

# 前端源码目录
FRONTEND_SRC = BASE_DIR / "frontend" / "src"

# 前端构建目录
FRONTEND_DIST_DIR = BASE_DIR / "frontend" / "dist"

# 虚拟环境目录（用于start.bat检查）
VENV_DIR = BACKEND_DIR / "venv"

# 前端node_modules目录（用于start.bat检查）
NODE_MODULES_DIR = BASE_DIR / "frontend" / "node_modules"

# ==================== 文件路径 ====================
# 认证文件路径：保存抖音登录态（storage_state格式）
AUTH_FILE = DATA_DIR / "douyin_auth.json"

# 视频数据文件路径：MVP阶段用JSON替代数据库
VIDEOS_FILE = DATA_DIR / "videos.json"

# Python依赖文件
REQUIREMENTS_FILE = BACKEND_DIR / "requirements.txt"

# 前端package.json
PACKAGE_JSON = BASE_DIR / "frontend" / "package.json"

# .env文件
ENV_FILE = BACKEND_DIR / ".env"

# 同步日志文件
SYNC_LOG_FILE = LOGS_DIR / "sync.log"

# 启动日志文件
START_LOG_FILE = LOGS_DIR / "start.log"

# ==================== URL配置 ====================
# 抖音主页
DOUYIN_HOME_URL = "https://www.douyin.com"

# 抖音个人主页（用于验证登录态）
DOUYIN_USER_URL = "https://www.douyin.com/user/self"

# 后端服务地址
BACKEND_HOST = "0.0.0.0"
BACKEND_PORT = 8000

# 前端开发服务器地址
FRONTEND_URL = "http://localhost:5173"

# ==================== AI 配置 ====================
# 智谱 AI / GLM-4-Flash
ZHIPUAI_API_KEY = os.getenv("ZHIPUAI_API_KEY", "")
ZHIPUAI_BASE_URL = os.getenv("ZHIPUAI_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")
ZHIPUAI_MODEL = os.getenv("ZHIPUAI_MODEL", "glm-4.7-flash")
ZHIPUAI_CHAT_URL = f"{ZHIPUAI_BASE_URL}/chat/completions"

# ==================== 浏览器配置 ====================
# Playwright反检测参数
# 为什么需要这些参数：抖音会检测自动化工具，这些参数可以绕过基础检测
BROWSER_ARGS = [
    "--disable-blink-features=AutomationControlled",
    "--disable-web-security",
    "--disable-features=IsolateOrigins,site-per-process",
    "--no-sandbox",
    "--disable-dev-shm-usage",
]

# 浏览器User-Agent
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

# 注入脚本：隐藏webdriver特征
# 为什么需要：navigator.webdriver=true是自动化工具的典型特征
STEALTH_JS = """
Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined
});
"""

# ==================== 同步配置 ====================
# 默认拉取视频数量限制
DEFAULT_SYNC_LIMIT = 10

# 最大同步视频数量
MAX_SYNC_LIMIT = 500

# 页面滚动等待时间（秒）
SCROLL_WAIT_MIN = 1.5
SCROLL_WAIT_MAX = 3.0


def ensure_dirs():
    """
    确保所有必要的目录存在
    为什么单独抽成函数：在应用启动时调用一次，避免运行时目录不存在
    """
    dirs_to_create = [DATA_DIR, LOGS_DIR]
    for dir_path in dirs_to_create:
        os.makedirs(dir_path, exist_ok=True)


def get_backend_cwd() -> str:
    """
    获取后端工作目录（用于start.bat切换目录）
    """
    return str(BACKEND_DIR)
