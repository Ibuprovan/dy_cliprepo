import json
import re
import httpx
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
            if not self._check_ollama_available():
                raise Exception(
                    "Ollama 服务未启动或不可用。请先安装并启动 Ollama：\n"
                    "1. 访问 https://ollama.ai 下载安装\n"
                    "2. 运行 'ollama serve' 启动服务\n"
                    "3. 运行 'ollama pull qwen2.5:14b' 拉取模型"
                )
            self.client = OpenAI(
                base_url=settings.OLLAMA_BASE_URL,
                api_key="ollama",
            )
            self.model = settings.OLLAMA_MODEL
        elif self.provider == "deepseek":
            if not settings.DEEPSEEK_API_KEY:
                raise Exception("DeepSeek API Key 未配置，请在 .env 文件中设置 DEEPSEEK_API_KEY")
            self.client = OpenAI(
                base_url=settings.DEEPSEEK_BASE_URL,
                api_key=settings.DEEPSEEK_API_KEY,
            )
            self.model = settings.DEEPSEEK_MODEL
        else:
            if not settings.OPENAI_API_KEY:
                raise Exception("OpenAI API Key 未配置，请在 .env 文件中设置 OPENAI_API_KEY")
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = settings.OPENAI_MODEL

    def _check_ollama_available(self) -> bool:
        try:
            base_url = settings.OLLAMA_BASE_URL.replace("/v1", "")
            response = httpx.get(f"{base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

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
                    timeout=60,
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
