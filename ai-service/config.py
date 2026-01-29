import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    LLM_API_URL: str = os.getenv("LLM_API_URL", "https://api.vveai.com")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-search-preview")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))


settings = Settings()
