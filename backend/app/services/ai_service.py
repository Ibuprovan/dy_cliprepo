import logging
import re
from typing import Tuple, Union

import httpx

from app.core.config import ZHIPUAI_API_KEY, ZHIPUAI_CHAT_URL, ZHIPUAI_MODEL

logger = logging.getLogger(__name__)

CATEGORIES = [
    "技术/编程", "生活vlog", "美食", "旅行", "游戏", "搞笑",
    "知识/教育", "音乐", "运动健身", "美妆时尚", "影视", "其他",
]

SYSTEM_PROMPT = (
    "你是一个抖音视频分析助手。总结视频内容，写一段有用的中文总结。\n"
    "要求：\n"
    "1. 总结必须基于实际内容，禁止重复标题和描述\n"
    "2. 100-200字，结构清晰，包含内容概述、要点和价值\n"
    "3. 最后从以下分类中选择最匹配的："
    + "、".join(CATEGORIES) +
    "\n格式：先写总结，再单独一行写【分类：xxx】"
)


async def generate_summary_and_category(
    title: str,
    desc: str = "",
    video_url: str = "",
) -> Tuple[str, str]:
    if not ZHIPUAI_API_KEY:
        return _fallback_summary(title, desc), "未分类"

    use_vl = bool(video_url and len(desc.strip()) < 50)

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
        user_content = f"标题：{title}\n描述：{desc}" if desc else f"标题：{title}"
        api_timeout = 30
        mode_tag = "TEXT"

    api_max_tokens = 4096

    logger.info(
        f"[{mode_tag}] AI 请求: title={title[:60]} desc_len={len(desc)} "
        f"video_url={'yes' if video_url else 'no'}"
    )

    try:
        async with httpx.AsyncClient(timeout=api_timeout) as client:
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
            response = await client.post(
                ZHIPUAI_CHAT_URL,
                headers={
                    "Authorization": f"Bearer {ZHIPUAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            message = data["choices"][0]["message"]

            # 关闭 thinking 后输出走 content，reasoning_content 做兜底
            raw = (
                message.get("content", "").strip()
                or message.get("reasoning_content", "").strip()
            )

            logger.debug(f"[{mode_tag}] AI 原始响应({len(raw)}字): {raw[:200]}...")
            summary, category = _parse_response(raw)
            logger.info(f"[{mode_tag}] 摘要 {len(summary)}字 | 分类 {category}")
            if summary and len(summary) < 20:
                logger.warning(f"[{mode_tag}] 摘要过短({len(summary)}字)，可能质量问题")
            return summary, category

    except httpx.TimeoutException:
        logger.error(f"GLM-4.6V-Flash API 请求超时 ({mode_tag})")
    except httpx.HTTPStatusError as e:
        logger.error(f"GLM-4.6V-Flash API 返回错误: {e.response.status_code} ({mode_tag})")
        logger.debug(f"错误响应: {e.response.text[:300]}")
    except Exception as e:
        logger.error(f"GLM-4.6V-Flash API 调用失败: {e} ({mode_tag})")
        logger.debug(f"请求 payload: title={title[:40]} desc_len={len(desc)}")

    return _fallback_summary(title, desc), "未分类"


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
        "vlog": "生活vlog", "生活": "生活vlog",
        "美食": "美食", "吃": "美食", "烹饪": "美食",
        "旅行": "旅行", "旅游": "旅行", "风景": "旅行",
        "游戏": "游戏", "电竞": "游戏",
        "搞笑": "搞笑", "幽默": "搞笑",
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


async def generate_summary(title: str, desc: str = "", video_url: str = "") -> str:
    summary, _ = await generate_summary_and_category(title, desc, video_url)
    return summary


def _fallback_summary(title: str, desc: str) -> str:
    return desc[:100] if desc else title[:100]
