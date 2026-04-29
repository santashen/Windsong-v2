from __future__ import annotations

import hmac
import time
from datetime import datetime, timezone
from hashlib import sha256

from fastapi import Header, HTTPException

from config import settings

PORTFOLIO_TOKEN_TTL_SECONDS = 12 * 60 * 60


def verify_admin_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> None:
    if settings.ADMIN_API_KEY == "":
        return

    provided_key = x_api_key or ""
    if not provided_key and authorization and authorization.startswith("Bearer "):
        provided_key = authorization[7:]

    if provided_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


def _extract_bearer_token(authorization: str | None) -> str:
    if authorization and authorization.startswith("Bearer "):
        return authorization[7:]
    return ""


def _portfolio_token_signature(expires_at: int) -> str:
    payload = f"family-portfolio:{expires_at}".encode("utf-8")
    secret = settings.PORTFOLIO_ACCESS_PASSWORD.encode("utf-8")
    return hmac.new(secret, payload, sha256).hexdigest()


def create_family_portfolio_access_token() -> dict:
    expires_at = int(time.time()) + PORTFOLIO_TOKEN_TTL_SECONDS
    signature = _portfolio_token_signature(expires_at)
    return {
        "access_token": f"{expires_at}.{signature}",
        "expires_at": datetime.fromtimestamp(expires_at, tz=timezone.utc).isoformat(),
        "access_required": bool(settings.PORTFOLIO_ACCESS_PASSWORD),
    }


def verify_family_portfolio_password(password: str) -> dict:
    configured_password = settings.PORTFOLIO_ACCESS_PASSWORD
    if not configured_password:
        return {"access_token": "", "expires_at": None, "access_required": False}

    if not hmac.compare_digest(password, configured_password):
        raise HTTPException(status_code=401, detail="访问密码不正确")

    return create_family_portfolio_access_token()


def verify_family_portfolio_access(
    x_portfolio_access_token: str | None = Header(default=None, alias="X-Portfolio-Access-Token"),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> None:
    if settings.ADMIN_API_KEY and x_api_key and hmac.compare_digest(x_api_key, settings.ADMIN_API_KEY):
        return

    if not settings.PORTFOLIO_ACCESS_PASSWORD:
        return

    token = x_portfolio_access_token or _extract_bearer_token(authorization)
    if not token or "." not in token:
        raise HTTPException(status_code=401, detail="请先输入家庭投资组合访问密码")

    expires_at_raw, signature = token.split(".", 1)
    try:
        expires_at = int(expires_at_raw)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="家庭投资组合访问已失效") from exc

    if expires_at < int(time.time()):
        raise HTTPException(status_code=401, detail="家庭投资组合访问已过期，请重新输入密码")

    expected_signature = _portfolio_token_signature(expires_at)
    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(status_code=401, detail="家庭投资组合访问已失效")
