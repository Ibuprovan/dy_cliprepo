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

# 视频封面（在视频项内查找图片 src）
VIDEO_COVER_SELECTORS = [
    'img[alt]',
    'img',
    '[class*="cover"] img',
]

# ==================== 视频详情页 ====================
# 详情页描述文本（通常更完整）
# 抖音页面结构：描述通常在 video-info 区域内的特定 class
VIDEO_DESC_DETAIL_SELECTORS = [
    '[class*="video-info"] [class*="desc"]',
    '[class*="video-info"] [class*="title"]',
    '[class*="desc-text"]',
    '[data-e2e*="video-desc"]',
    '[class*="video-detail"]',
    # 兜底：通用选择器
    '[class*="desc"]',
    '[class*="title"]',
]

# 视频源地址（video 标签内的 src）
VIDEO_SOURCE_SELECTORS = [
    'video[src]',
    'video source[src]',
]

# 详情页已知错误关键词（页面加载异常时跳过）
VIDEO_PAGE_ERROR_KEYWORDS = [
    "页面不见了",
    "页面不存在",
    "页面找不到了",
    "没有找到",
    "页面失效",
    "该视频已被作者删除",
]

# 详情页无意义文本过滤（跳过导航栏/搜索等 UI 文本）
VIDEO_PAGE_NOISE_KEYWORDS = [
    "搜索",
    "登录",
    "注册",
    "关注",
    "点赞",
    "评论",
    "分享",
    "首页",
    "推荐",
    "朋友",
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
