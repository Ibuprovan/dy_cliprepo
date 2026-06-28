import logging
from typing import Optional, Tuple

import httpx

from app.core.config import ZHIPUAI_API_KEY, ZHIPUAI_CHAT_URL, ZHIPUAI_MODEL

logger = logging.getLogger(__name__)

CATEGORY_SEPARATOR = "===CATEGORY==="

CATEGORIES = [
    "技术/编程", "生活vlog", "美食", "旅行", "游戏", "搞笑",
    "知识/教育", "音乐", "运动健身", "美妆时尚", "影视", "其他",
]

SYSTEM_PROMPT = (
    "你是一个抖音视频内容分析助手。根据给定的视频标题和描述，完成两项任务：\n"
    "1. 用一段流畅的中文完整总结视频的核心内容，包括主要观点、要点和结论。"
    "要求：100-200字，结构清晰，不要加'这个视频'之类的开头词。\n"
    "2. 从以下分类中选择最合适的一个：\n"
    + ", ".join(CATEGORIES) + "\n"
    "输出格式：\n"
    "摘要内容...\n"
    f"{CATEGORY_SEPARATOR}\n"
    "分类名称\n"
    "注意：摘要中不要包含分类信息，分类单独放在分隔符后面。"
)


async def generate_summary_and_category(title: str, desc: str) -> Tuple[str, str]:
    """
    调用 GLM-4.7-Flash 生成视频摘要和分类
    返回 (summary, category)
    """
    if not ZHIPUAI_API_KEY:
        logger.warning("ZHIPUAI_API_KEY 未配置，使用后备摘要")
        return _fallback_summary(title, desc), "未分类"

    user_content = f"标题：{title}\n描述：{desc}" if desc else f"标题：{title}"

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                ZHIPUAI_CHAT_URL,
                headers={
                    "Authorization": f"Bearer {ZHIPUAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": ZHIPUAI_MODEL,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_content},
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2048,
                },
            )
            response.raise_for_status()
            data = response.json()
            message = data["choices"][0]["message"]
            raw = (
                message.get("content", "").strip()
                or message.get("reasoning_content", "").strip()
            )
            summary, category = _parse_response(raw)
            logger.info(f"AI 摘要+分类成功: {summary[:30]}... | {category}")
            return summary, category

    except httpx.TimeoutException:
        logger.error("GLM-4-Flash API 请求超时")
    except httpx.HTTPStatusError as e:
        logger.error(f"GLM-4-Flash API 返回错误: {e.response.status_code}")
    except Exception as e:
        logger.error(f"GLM-4-Flash API 调用失败: {e}")

    return _fallback_summary(title, desc), "未分类"


def _clean_thinking(text: str) -> str:
    """从 GLM-4.7-Flash 推理输出中提取最终答案"""
    if not text:
        return ""

    import re

    # 策略1: 中文引号
    cn_quoted = re.findall('\u201c([^\u201d]+)\u201d', text)
    candidates = [q.strip() for q in cn_quoted if len(q.strip()) >= 15]
    if candidates:
        return candidates[-1][:300]

    # 策略2: 尾部英文引号
    all_quoted = re.findall('"([^"]+)"', text)
    long_quoted = [q.strip() for q in all_quoted if len(q.strip()) >= 20 and len(q.strip()) <= 300]
    if long_quoted:
        return long_quoted[-1][:300]

    # 策略3: 标记词后的尾段
    markers = ['最终输出', '最终答案', '最终润色', '最终总结', '最终选择']
    for marker in markers:
        if marker in text:
            idx = text.rfind(marker)
            snippet = text[idx + len(marker):][:400]
            q = re.findall('\u201c([^\u201d]+)\u201d', snippet)
            if not q:
                q = re.findall('"([^"]{10,300})"', snippet)
            if q:
                return q[-1].strip()[:300]
            lines = [l.strip() for l in snippet.split('\n') if l.strip() and not l.strip().startswith('*')]
            for line in lines:
                if len(line) >= 15:
                    return line[:300]

    # 策略4: 最后回退
    parts = [p.strip() for p in text.split('\n\n') if p.strip()]
    for part in reversed(parts):
        clean = part.strip('"*\n ')
        if len(clean) >= 15 and not clean[0].isdigit():
            return clean[:300]

    return text[:300]


def _parse_response(raw: str) -> Tuple[str, str]:
    """从 AI 返回的原始内容中解析摘要和分类"""
    if CATEGORY_SEPARATOR in raw:
        parts = raw.split(CATEGORY_SEPARATOR)
        summary_part = parts[0].strip()
        category_part = parts[1].strip() if len(parts) > 1 else ""
        summary = _clean_thinking(summary_part)
        category = _match_category(category_part)
        return summary, category

    # 没有分隔符，尝试在 reasoning 输出中提取
    cleaned = _clean_thinking(raw)
    return cleaned, "未分类"


def _match_category(text: str) -> str:
    """从文本中匹配最接近的预设分类"""
    text = text.strip()
    # 直接匹配
    for cat in CATEGORIES:
        if cat in text:
            return cat
    # 模糊匹配（取第一个出现的分类关键词）
    keywords = {
        "技术": "技术/编程", "编程": "技术/编程", "代码": "技术/编程",
        "vlog": "生活vlog", "生活": "生活vlog",
        "美食": "美食", "吃": "美食", "烹饪": "美食",
        "旅行": "旅行", "旅游": "旅行", "风景": "旅行",
        "游戏": "游戏", "电竞": "游戏",
        "搞笑": "搞笑", "幽默": "搞笑", "段子": "搞笑",
        "知识": "知识/教育", "教育": "知识/教育", "学习": "知识/教育", "科普": "知识/教育",
        "音乐": "音乐", "唱歌": "音乐",
        "运动": "运动健身", "健身": "运动健身",
        "美妆": "美妆时尚", "穿搭": "美妆时尚", "时尚": "美妆时尚",
        "影视": "影视", "电影": "影视", "电视剧": "影视",
    }
    for keyword, cat in keywords.items():
        if keyword in text:
            return cat
    return "其他"


async def generate_summary(title: str, desc: str) -> str:
    """兼容旧接口：只返回摘要"""
    summary, _ = await generate_summary_and_category(title, desc)
    return summary


def _fallback_summary(title: str, desc: str) -> str:
    return desc[:100] if desc else title[:100]
