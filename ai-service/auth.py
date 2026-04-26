from __future__ import annotations

from fastapi import Header, HTTPException

from config import settings


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
