import asyncio
import logging
import re
from typing import Tuple, Union

import httpx

from app.core.config import ZHIPUAI_API_KEY, ZHIPUAI_CHAT_URL, ZHIPUAI_MODEL

logger = logging.getLogger(__name__)

_PLAYER_TIME_RE = re.compile(r'\d{1,2}:\d{2}(?::\d{2})?\s*/\s*\d{1,2}:\d{2}(?::\d{2})?')


def _looks_like_player_ui(text: str) -> bool:
    """描述文本含播放器 UI 特征时视为无效"""
    if _PLAYER_TIME_RE.search(text):
        return True
    if "倍速" in text and ("清屏" in text or "连播" in text):
        return True
    return False


CATEGORIES = [
    "技术/编程", "生活vlog", "美食", "旅行", "游戏", "搞笑",
    "知识/教育", "音乐", "运动健身", "美妆时尚", "影视", "其他",
]

SYSTEM_PROMPT = (
    "你是一个抖音视频分析助手。总结视频内容，写一段有用的中文总结。\n"
    "要求：\n"
    "1. 总结必须基于实际内容，禁止重复标题和描述的原文\n"
    "2. 100-200字，结构清晰，包含内容概述、要点和价值\n"
    "3. 最后从以下分类中选择最匹配的："
    + "、".join(CATEGORIES) +
    "\n格式：先写总结，再单独一行写【分类：xxx】"
)

# 重试配置
MAX_RETRIES = 3
RETRY_BASE_DELAY = 2.0  # 首次重试等待 2 秒，之后递增


async def _call_glm_api(payload: dict, timeout: int) -> Tuple[str, bool]:
    """
    单次调用 GLM API，返回 (响应文本, 是否成功)
    失败时返回 ("", False)
    """
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                ZHIPUAI_CHAT_URL,
                headers={
                    "Authorization": f"Bearer {ZHIPUAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )

            # 429 限流：抛出特定异常供上层重试
            if response.status_code == 429:
                logger.warning("GLM API 返回 429 限流，将重试")
                return "", False

            response.raise_for_status()
            data = response.json()
            message = data["choices"][0]["message"]

            # 关闭 thinking 后输出走 content，reasoning_content 做兜底
            raw = (
                message.get("content", "").strip()
                or message.get("reasoning_content", "").strip()
            )
            return raw, True

    except httpx.TimeoutException:
        logger.error("GLM API 请求超时")
        return "", False
    except httpx.HTTPStatusError as e:
        logger.error(f"GLM API 返回错误: {e.response.status_code}")
        return "", False
    except Exception as e:
        logger.error(f"GLM API 调用失败: {e}")
        return "", False


async def _call_with_retry(payload: dict, timeout: int, mode_tag: str) -> str:
    """
    带重试机制的 API 调用。
    遇到 429 或失败时，等待递增延迟后重试，最多 MAX_RETRIES 次。
    """
    for attempt in range(MAX_RETRIES):
        raw, success = await _call_glm_api(payload, timeout)
        if success and raw:
            return raw

        if attempt < MAX_RETRIES - 1:
            delay = RETRY_BASE_DELAY * (attempt + 1)
            logger.info(f"[{mode_tag}] 第 {attempt + 1} 次调用失败，{delay}s 后重试...")
            await asyncio.sleep(delay)

    logger.error(f"[{mode_tag}] API 调用 {MAX_RETRIES} 次均失败")
    return ""


async def generate_summary_and_category(
    title: str,
    desc: str = "",
    video_url: str = "",
) -> Tuple[str, str]:
    if not ZHIPUAI_API_KEY:
        logger.warning("ZHIPUAI_API_KEY 未配置，使用本地兜底")
        return _local_fallback(title, desc)

    # 过滤播放器 UI 文本（二次防护）
    if _looks_like_player_ui(desc):
        desc = ""

    # 路由判断：VL 模式需要 video_url 且描述极短
    # 降低 VL 触发门槛：只有 desc 完全为空且有 video_url 时才走 VL
    use_vl = bool(video_url and not desc.strip())

    if use_vl:
        user_content: Union[str, list] = [
            {"type": "video_url", "video_url": {"url": video_url}},
            {"type": "text", "text": (
                f"视频标题：{title}\n\n"
                "根据这个视频的画面和内容写一段中文总结，100-200字。"
            )},
        ]
        api_timeout = 120
        mode_tag = "VL"
    else:
        # TEXT 模式：即使 desc 很短，也用 title+desc 一起送
        user_content = f"标题：{title}\n描述：{desc}" if desc.strip() else f"标题：{title}\n请根据标题总结视频内容。"
        api_timeout = 30
        mode_tag = "TEXT"

    api_max_tokens = 4096

    logger.info(
        f"[{mode_tag}] AI 请求: title={title[:60]} desc_len={len(desc)} "
        f"video_url={'yes' if video_url else 'no'}"
    )

    payload = {
        "model": ZHIPUAI_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        "temperature": 0.7,
        "max_tokens": api_max_tokens,
        "thinking": {"type": "disabled"},
    }

    raw = await _call_with_retry(payload, api_timeout, mode_tag)

    if raw:
        logger.debug(f"[{mode_tag}] AI 原始响应({len(raw)}字): {raw[:200]}...")
        summary, category = _parse_response(raw)
        logger.info(f"[{mode_tag}] 摘要 {len(summary)}字 | 分类 {category}")

        # 质量检查：如果摘要过短或等于原文截取，使用本地兜底
        if len(summary) < 20:
            logger.warning(f"[{mode_tag}] 摘要过短({len(summary)}字)，使用本地兜底")
            return _local_fallback(title, desc)

        return summary, category

    # API 调用完全失败，使用本地兜底
    logger.warning(f"[{mode_tag}] API 调用失败，使用本地兜底")
    return _local_fallback(title, desc)


def _parse_response(raw: str) -> Tuple[str, str]:
    category = _match_category(raw)
    summary = _extract_summary(raw)
    return summary, category


def _extract_summary(text: str) -> str:
    """从模型输出中提取总结段落"""
    if not text:
        return ""

    # 策略1：按 【分类：xxx】 分割，取之前的内容
    # 模型被要求以 "【分类：xxx】" 结尾，这是最可靠的提取方式
    m = re.split(r'【分类[：:]\s*', text)
    if len(m) >= 2:
        before = m[0].strip()
        paragraphs = [p.strip() for p in re.split(r'\n\n+', before) if p.strip()]
        for p in reversed(paragraphs):
            p = p.strip('"*\u201c\u201d \n\t')
            if len(p) >= 30:
                return p[:400]
        if len(before) >= 20:
            return before[:400]

    # 策略2：中文引号内的内容
    cn = re.findall('\u201c([^\u201d]+)\u201d', text)
    long_cn = [q.strip() for q in cn if len(q.strip()) >= 30]
    if long_cn:
        return long_cn[-1][:400]

    # 策略3：英文引号
    en = re.findall('"([^"]{30,300})"', text)
    if en:
        return en[-1].strip()[:400]

    # 策略4：最后一个非序号段落
    parts = [p.strip() for p in re.split(r'\n\n+', text) if p.strip()]
    for part in reversed(parts):
        clean = part.strip('"* \n')
        if len(clean) >= 30 and not clean[0].isdigit():
            return clean[:400]

    # 策略5：最后一句完整的中文句子
    sentences = re.split(r'[。！？\n]', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    for s in reversed(sentences):
        if len(s) >= 30:
            return s[:400]

    return text[:400]


def _match_category(text: str) -> str:
    """从文本中扫描所有分类关键词（全文扫描，不限位置）"""
    text = text.strip()
    for cat in CATEGORIES:
        if cat in text:
            return cat
    keywords = {
        "技术": "技术/编程", "编程": "技术/编程", "代码": "技术/编程",
        "前端": "技术/编程", "AI": "技术/编程", "工具": "技术/编程",
        "软件": "技术/编程", "开源": "技术/编程", "程序": "技术/编程",
        "vlog": "生活vlog", "生活": "生活vlog",
        "美食": "美食", "吃": "美食", "烹饪": "美食",
        "旅行": "旅行", "旅游": "旅行", "风景": "旅行",
        "游戏": "游戏", "电竞": "游戏",
        "搞笑": "搞笑", "幽默": "搞笑",
        "知识": "知识/教育", "教育": "知识/教育", "学习": "知识/教育", "科普": "知识/教育",
        "数学建模": "知识/教育", "论文": "知识/教育", "备赛": "知识/教育",
        "音乐": "音乐", "唱歌": "音乐",
        "运动": "运动健身", "健身": "运动健身",
        "美妆": "美妆时尚", "穿搭": "美妆时尚", "时尚": "美妆时尚",
        "影视": "影视", "电影": "影视", "电视剧": "影视",
        "装修": "生活vlog", "职场": "知识/教育", "面试": "知识/教育",
        "求职": "知识/教育", "婚姻": "生活vlog", "情感": "生活vlog",
    }
    for keyword, cat in keywords.items():
        if keyword in text:
            return cat
    return "其他"


async def generate_summary(title: str, desc: str = "", video_url: str = "") -> str:
    summary, _ = await generate_summary_and_category(title, desc, video_url)
    return summary


def _local_fallback(title: str, desc: str) -> Tuple[str, str]:
    """
    本地兜底策略：当 AI 调用完全失败时使用。
    基于标题和描述做智能提取，而不是生硬截取前100字。
    同时基于关键词做本地分类匹配。
    """
    # 分类兜底：基于标题+描述的关键词匹配
    combined_text = f"{title} {desc}"
    category = _match_category(combined_text)

    # 摘要兜底：智能提取
    summary = _smart_extract(title, desc)

    return summary, category


def _smart_extract(title: str, desc: str) -> str:
    """
    智能提取摘要：从描述中提取有意义的内容段落，而不是生硬截取前100字。
    """
    if not desc.strip():
        return title.strip()

    # 清理描述：去掉 hashtag、多余空白
    cleaned = re.sub(r'#[^\s#]+', '', desc).strip()
    cleaned = re.sub(r'\s+', ' ', cleaned)

    if not cleaned:
        return title.strip()

    # 如果描述很短（< 150字），直接用清理后的描述
    if len(cleaned) <= 150:
        return cleaned

    # 如果描述很长，提取第一段有意义的内容
    # 按句号/换行分段，取前几句组成摘要
    sentences = re.split(r'[。！？\n]', cleaned)
    sentences = [s.strip() for s in sentences if len(s.strip()) >= 10]

    if not sentences:
        return cleaned[:150]

    # 取前 2-3 句，总长度控制在 100-200 字
    result = []
    total = 0
    for s in sentences:
        if total + len(s) > 200:
            break
        result.append(s)
        total += len(s)

    summary = "。".join(result)
    if summary and not summary.endswith(("。", "！", "？")):
        summary += "。"

    return summary[:400]
