import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    LLM_API_URL: str = os.getenv("LLM_API_URL", "https://api.vveai.com")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-search-preview")
    AKSHARE_PROXY_HOST: str = os.getenv("AKSHARE_PROXY_HOST", "101.201.173.125")
    AKSHARE_PROXY_TOKEN: str = os.getenv("AKSHARE_PROXY_TOKEN", "")
    AKSHARE_PROXY_RETRY: int = int(os.getenv("AKSHARE_PROXY_RETRY", "30"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    ENV: str = os.getenv("ENV", "development")


settings = Settings()
