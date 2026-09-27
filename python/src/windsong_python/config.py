import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    llm_api_url: str = os.getenv("LLM_API_URL", "").rstrip("/")
    llm_api_key: str = os.getenv("LLM_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "")
    llm_timeout_seconds: float = float(os.getenv("LLM_TIMEOUT_SECONDS", "120"))


settings = Settings()
