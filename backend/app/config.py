import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'data' / 'douyin_kb.db'}"
    CHROMADB_PATH: str = str(BASE_DIR / "data" / "chromadb")
    AUTH_DIR: str = str(BASE_DIR / "auth")

    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "ollama")

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")

    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5:14b")

    OPENAI_MODEL: str = "gpt-4o-mini"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"

    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))

    class Config:
        env_file = ".env"


settings = Settings()
