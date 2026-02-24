import json
import time
import uuid
from datetime import datetime, timedelta

import structlog
from fastapi import FastAPI, HTTPException, Query, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from config import settings
from logging_config import configure_logging
from services.base_llm import OpenAICompatibleService
from services.finance_data import FinanceDataService
from services.gold_analysis import GoldAnalysisService

configure_logging()
logger = structlog.get_logger()

app = FastAPI(title="Windsong AI Service", version="1.0.0")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that assigns a request_id and logs each request."""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        )

        start = time.perf_counter()
        response: Response = await call_next(request)
        latency_ms = round((time.perf_counter() - start) * 1000, 2)

        response.headers["X-Request-ID"] = request_id

        log = logger.bind(
            status=response.status_code,
            latency_ms=latency_ms,
            ip=request.client.host if request.client else "",
        )
        if response.status_code >= 500:
            log.error("request completed")
        elif response.status_code >= 400:
            log.warning("request completed")
        else:
            log.info("request completed")

        return response


# 错误码映射，与 Go 后端保持一致
_HTTP_TO_CODE: dict[int, int] = {
    400: 40000,
    401: 40100,
    403: 40100,
    404: 40400,
    422: 40001,
}
_SKIP_PATHS = {"/health"}


class ResponseEnvelopeMiddleware(BaseHTTPMiddleware):
    """将所有 /api/* JSON 响应包装为统一信封 {code, message, data}。"""

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)

        # 健康检查端点保持原始格式（供 Docker/Nginx 基础设施使用）
        if request.url.path in _SKIP_PATHS:
            return response

        # 只处理 JSON 响应
        content_type = response.headers.get("content-type", "")
        if "application/json" not in content_type:
            return response

        # 读取流式响应体
        chunks: list[bytes] = []
        async for chunk in response.body_iterator:
            if isinstance(chunk, str):
                chunk = chunk.encode("utf-8")
            chunks.append(chunk)
        body = b"".join(chunks)

        try:
            original = json.loads(body)
        except Exception:
            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=content_type,
            )

        status = response.status_code

        if status < 400:
            envelope = {"code": 0, "message": "success", "data": original}
        else:
            code = _HTTP_TO_CODE.get(status, 50000)
            if isinstance(original, dict) and "detail" in original:
                detail = original["detail"]
                message = detail if isinstance(detail, str) else str(detail)
            else:
                message = "error"
            envelope = {"code": code, "message": message}

        new_body = json.dumps(envelope).encode("utf-8")
        headers = dict(response.headers)
        headers["content-length"] = str(len(new_body))

        return Response(
            content=new_body,
            status_code=status,
            headers=headers,
            media_type="application/json",
        )


app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(ResponseEnvelopeMiddleware)

# Initialize services
llm_service = OpenAICompatibleService(
    api_url=settings.LLM_API_URL,
    api_key=settings.LLM_API_KEY,
    model=settings.LLM_MODEL,
)
gold_service = GoldAnalysisService(llm_service)
finance_service = FinanceDataService()


@app.get("/health")
async def health():
    return {"status": "ok", "service": "ai-service"}


@app.get("/api/test")
async def test_llm():
    """Simple test to verify LLM API connectivity."""
    try:
        response = await llm_service.generate("Say 'Hello, connection successful!' in one short sentence.")
        return {
            "status": "ok",
            "model": llm_service.get_model_name(),
            "response": response,
        }
    except Exception as e:
        logger.error("LLM test failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"LLM connection failed: {str(e)}")


@app.get("/api/gold/analyze")
async def analyze_gold():
    try:
        result = await gold_service.analyze()
        return result
    except Exception as e:
        logger.error("gold analysis failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/finance/search")
async def finance_search(keyword: str = Query(..., min_length=1)):
    """Search stocks and funds by keyword."""
    try:
        results = finance_service.search(keyword)
        return {"results": results}
    except Exception as e:
        logger.error("finance search failed", error=str(e), keyword=keyword)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/finance/history")
async def finance_history(
    codes: str = Query(..., description="Comma-separated codes"),
    type: str = Query("stock", description="stock or fund"),
    start: str = Query(None, description="Start date YYYY-MM-DD"),
    end: str = Query(None, description="End date YYYY-MM-DD"),
):
    """Fetch historical data for one or more codes."""
    if not end:
        end = datetime.now().strftime("%Y-%m-%d")
    if not start:
        start = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

    code_list = [c.strip() for c in codes.split(",") if c.strip()]
    if not code_list:
        raise HTTPException(status_code=400, detail="No codes provided")

    results = []
    for code in code_list:
        try:
            data = finance_service.get_history(code, type, start, end)
            results.append(data)
        except Exception as e:
            logger.error("failed to fetch history", code=code, error=str(e))
            results.append({"code": code, "type": type, "error": str(e)})

    return {"results": results}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
