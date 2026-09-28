import json
import logging
import re
from typing import Any

import httpx
from fastapi import HTTPException

from windsong_python.config import Settings, settings
from windsong_python.models.photo_metadata import ParseResponse

logger = logging.getLogger(__name__)


def extract_json(text: str) -> dict[str, Any]:
    """Accept a JSON response even when a compatible model adds markdown fences."""
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
    candidate = fenced.group(1) if fenced else text.strip()
    try:
        value = json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=502, detail="Python service returned invalid JSON") from exc
    if not isinstance(value, dict) or not isinstance(value.get("items"), list):
        raise HTTPException(status_code=502, detail="Python service returned an invalid photo list")
    return value


def build_prompt(content: str) -> str:
    return f"""你是照片资料整理助手。请把用户输入的非结构化照片信息拆分成照片列表，并只返回 JSON，不要返回 Markdown。

要求：
1. 每张照片必须是一个 items 元素；根据图片 URL、编号、空行或语义自然拆分。
2. 只提取用户明确提供的信息，不要猜测日期、城市、国家或拍摄地点。
3. 日期统一为 YYYY-MM-DD；无法确定时返回空字符串，并在 warnings 中说明。
4. tags 必须是字符串数组；没有标签时返回空数组。
5. 缺失 url、title、date 时，将字段名加入 missingFields。
6. 输出格式必须是 {{"items": [{{"index": 1, "status": "ready", "url": "", "thumbnail": "", "title": "", "description": "", "date": "", "location": "", "city": "", "country": "", "tags": [], "aspectRatio": "", "warnings": [], "missingFields": []}}]}}。

用户输入：
{content}
"""


class PhotoMetadataService:
    def __init__(self, service_settings: Settings = settings) -> None:
        self.settings = service_settings

    async def parse(self, content: str) -> ParseResponse:
        if not self.settings.llm_api_url or not self.settings.llm_api_key or not self.settings.llm_model:
            raise HTTPException(status_code=503, detail="LLM service is not configured")

        messages = [
            {"role": "system", "content": "你只输出符合要求的 JSON。"},
            {"role": "user", "content": build_prompt(content)},
        ]
        try:
            async with httpx.AsyncClient(timeout=self.settings.llm_timeout_seconds) as client:
                response = await client.post(
                    f"{self.settings.llm_api_url}/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.settings.llm_api_key}"},
                    json={
                        "model": self.settings.llm_model,
                        "messages": messages,
                        "temperature": 0.1,
                        "stream": False,
                    },
                )
                response.raise_for_status()
                body = response.json()
                text = body["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as exc:
            upstream_body = exc.response.text[:1000].replace("\n", " ")
            logger.error(
                "LLM upstream returned an error: status=%s body=%s",
                exc.response.status_code,
                upstream_body,
            )
            raise HTTPException(status_code=502, detail="LLM upstream request failed") from exc
        except httpx.RequestError as exc:
            logger.error("LLM request could not be completed: %s", exc)
            if isinstance(exc, httpx.TimeoutException):
                raise HTTPException(status_code=504, detail="LLM request timed out") from exc
            raise HTTPException(status_code=502, detail="LLM request could not be completed") from exc
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            logger.error("LLM returned an unexpected response: %s", exc)
            raise HTTPException(status_code=502, detail="LLM returned an unexpected response") from exc

        return ParseResponse.model_validate(extract_json(text))
