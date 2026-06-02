import json
import re
from typing import Optional
from openai import OpenAI

from app.config import settings
from app.ai.prompts import SUMMARY_PROMPT, EMPTY_DESC_PROMPT


class AIProcessor:
    def __init__(self, provider: Optional[str] = None):
        self.provider = provider or settings.AI_PROVIDER
        self._init_client()

    def _init_client(self):
        if self.provider == "ollama":
            self.client = OpenAI(
                base_url=settings.OLLAMA_BASE_URL,
                api_key="ollama",
            )
            self.model = settings.OLLAMA_MODEL
        elif self.provider == "deepseek":
            self.client = OpenAI(
                base_url=settings.DEEPSEEK_BASE_URL,
                api_key=settings.DEEPSEEK_API_KEY,
            )
            self.model = settings.DEEPSEEK_MODEL
        else:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = settings.OPENAI_MODEL

    async def process_video(self, title: str, desc: str, author: str) -> dict:
        if desc and desc.strip():
            prompt = SUMMARY_PROMPT.format(title=title, desc=desc, author=author)
        else:
            prompt = EMPTY_DESC_PROMPT.format(title=title, author=author)

        for attempt in range(3):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                )

                content = response.choices[0].message.content
                result = self._parse_json(content)

                if result:
                    return {
                        "summary": result.get("summary", ""),
                        "category": result.get("category", "其他"),
                        "tags": result.get("tags", []),
                        "key_points": result.get("key_points", []),
                        "quality_score": result.get("quality_score", 5),
                    }
            except Exception as e:
                if attempt == 2:
                    return {
                        "summary": f"AI处理失败: {str(e)}",
                        "category": "其他",
                        "tags": [],
                        "key_points": [],
                        "quality_score": 1,
                    }

        return {
            "summary": "AI处理失败",
            "category": "其他",
            "tags": [],
            "key_points": [],
            "quality_score": 1,
        }

    @staticmethod
    def _parse_json(text: str) -> Optional[dict]:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

        return None
