# backend/app/scraper/selectors.py
"""
CSS 选择器集中管理
抖音 DOM 结构会变化，集中管理便于更新

更新记录：
- 2026-06-23: 初始版本
"""

# ==================== 视频列表 ====================
# 收藏页面视频列表容器
VIDEO_LIST_SELECTORS = [
    '[data-e2e="scroll-list"] > li',
    '[data-e2e="user-post-list"] > div',
    'ul li',
]

# ==================== 视频元素 ====================
# 视频链接
VIDEO_LINK_SELECTORS = [
    "a[href*='/video/']",
    "a",
]

# 视频标题（优先从 img alt 属性获取）
VIDEO_TITLE_SELECTORS = [
    'img[alt]',
    'p[class]',
    '[class*="title"]',
]

# 视频描述
VIDEO_DESC_SELECTORS = [
    'p._ovpgIXn',  # 特定 class 的 p 标签（可能过期）
    'p[class]',
]

# ==================== 收藏页面 ====================
# 收藏标签按钮
FAVORITE_TAB_SELECTORS = [
    '[data-e2e="user-tab-favorite"]',
    'text="收藏"',
    '[class*="favorite"]',
    '[class*="collect"]',
]

# ==================== 登录状态 ====================
# 登录成功的标志文本
LOGIN_INDICATORS = [
    "我的主页",
    "个人主页",
    "退出登录",
    "我的收藏",
    "关注",
    "粉丝",
]
