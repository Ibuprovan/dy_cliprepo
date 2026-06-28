import logging
from typing import Optional

import httpx

from app.core.config import ZHIPUAI_API_KEY, ZHIPUAI_CHAT_URL, ZHIPUAI_MODEL

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "你是一个抖音视频内容总结助手。根据给定的视频标题和描述，用一句简洁的中文概括视频核心内容。"
    "要求：30-50字，直接给出总结内容，不要加'这个视频'之类的开头词。"
)


async def generate_summary(title: str, desc: str) -> str:
    """
    调用 GLM-4.7-Flash 生成视频摘要
    """
    if not ZHIPUAI_API_KEY:
        logger.warning("ZHIPUAI_API_KEY 未配置，使用后备摘要")
        return _fallback_summary(title, desc)

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
                    "max_tokens": 1024,
                },
            )
            response.raise_for_status()
            data = response.json()
            message = data["choices"][0]["message"]
            summary = (
                message.get("content", "").strip()
                or message.get("reasoning_content", "").strip()
            )
            summary = _clean_thinking(summary)
            logger.info(f"AI 摘要生成成功: {summary[:40]}...")
            return summary

    except httpx.TimeoutException:
        logger.error("GLM-4-Flash API 请求超时")
        return _fallback_summary(title, desc)
    except httpx.HTTPStatusError as e:
        logger.error(f"GLM-4-Flash API 返回错误: {e.response.status_code}")
        return _fallback_summary(title, desc)
    except Exception as e:
        logger.error(f"GLM-4-Flash API 调用失败: {e}")
        return _fallback_summary(title, desc)


def _fallback_summary(title: str, desc: str) -> str:
    if desc:
        return desc[:100]
    return title[:100]


def _clean_thinking(text: str) -> str:
    """从 GLM-4.7-Flash 推理输出中提取最终答案"""
    if not text:
        return ""

    import re

    # 策略1: 中文引号（智谱模型可能用这个）
    cn_quoted = re.findall('\u201c([^\u201d]+)\u201d', text)
    candidates = [q.strip() for q in cn_quoted if len(q.strip()) >= 15]
    if candidates:
        return candidates[-1][:100]

    # 策略2: 尾部英文引号 — 取最后一个长度合适的引用
    all_quoted = re.findall('"([^"]+)"', text)
    long_quoted = [q.strip() for q in all_quoted if len(q.strip()) >= 20 and len(q.strip()) <= 80]
    if long_quoted:
        return long_quoted[-1][:100]

    # 策略3: 标记词后的尾段
    markers = ['最终输出', '最终答案', '最终润色', '最终总结', '最终选择']
    for marker in markers:
        if marker in text:
            idx = text.rfind(marker)
            snippet = text[idx + len(marker):][:200]
            # 在 snippet 中找引号内容
            q = re.findall('\u201c([^\u201d]+)\u201d', snippet)
            if not q:
                q = re.findall('"([^"]{10,80})"', snippet)
            if q:
                return q[-1].strip()[:100]
            # 没引号就取第一段有意义的文本
            lines = [l.strip() for l in snippet.split('\n') if l.strip() and not l.strip().startswith('*')]
            for line in lines:
                if len(line) >= 15:
                    return line[:100]

    # 策略4: 最后回退
    parts = [p.strip() for p in text.split('\n\n') if p.strip()]
    for part in reversed(parts):
        clean = part.strip('"*\n ')
        if len(clean) >= 15 and not clean[0].isdigit():
            return clean[:100]

    return text[:100]
