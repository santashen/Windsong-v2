import os
from dotenv import load_dotenv

load_dotenv()


def env_bool(name: str, default: bool) -> bool:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


class Settings:
    DB_USER: str = os.getenv("DB_USER", "windsong")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "windsong123")
    DB_NAME: str = os.getenv("DB_NAME", "windsong")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    ADMIN_API_KEY: str = os.getenv("ADMIN_API_KEY", "")
    PORTFOLIO_ACCESS_PASSWORD: str = os.getenv("PORTFOLIO_ACCESS_PASSWORD", "")
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
    FAMILY_PORTFOLIO_SYNC_ENABLED: bool = env_bool("FAMILY_PORTFOLIO_SYNC_ENABLED", True)
    FAMILY_PORTFOLIO_SYNC_HOUR: int = int(os.getenv("FAMILY_PORTFOLIO_SYNC_HOUR", "23"))
    FAMILY_PORTFOLIO_SYNC_MINUTE: int = int(os.getenv("FAMILY_PORTFOLIO_SYNC_MINUTE", "0"))
    FAMILY_PORTFOLIO_SYNC_TIMEZONE: str = os.getenv("FAMILY_PORTFOLIO_SYNC_TIMEZONE", "Asia/Shanghai")
    FAMILY_PORTFOLIO_BENCHMARK_SYMBOL: str = os.getenv("FAMILY_PORTFOLIO_BENCHMARK_SYMBOL", "sh000300")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    ENV: str = os.getenv("ENV", "development")


settings = Settings()
