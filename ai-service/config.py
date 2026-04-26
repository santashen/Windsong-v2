import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    DB_USER: str = os.getenv("DB_USER", "windsong")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "windsong123")
    DB_NAME: str = os.getenv("DB_NAME", "windsong")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"host={DB_HOST} user={DB_USER} password={DB_PASSWORD} dbname={DB_NAME} port={DB_PORT} sslmode=disable",
    )
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
