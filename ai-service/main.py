import time
import uuid

import structlog
from fastapi import FastAPI, HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from config import settings
from logging_config import configure_logging
from services.base_llm import OpenAICompatibleService
from services.valuation_backtest import ValuationBacktestService

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


app.add_middleware(RequestLoggingMiddleware)

# Initialize services
llm_service = OpenAICompatibleService(
    api_url=settings.LLM_API_URL,
    api_key=settings.LLM_API_KEY,
    model=settings.LLM_MODEL,
)
valuation_service = ValuationBacktestService()


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


@app.get("/api/valuation-backtest")
async def valuation_backtest(symbol: str, start_date: str | None = None, end_date: str | None = None):
    try:
        data = valuation_service.get_backtest(symbol=symbol, start_date=start_date, end_date=end_date)
        return {
            "symbol": symbol,
            "start_date": start_date,
            "end_date": end_date,
            "data": data,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("valuation backtest failed", symbol=symbol, start_date=start_date, end_date=end_date)
        raise HTTPException(status_code=500, detail=f"估值回测失败: {str(exc)}") from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
