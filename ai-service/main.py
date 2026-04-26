import time
import uuid

import structlog
from fastapi import FastAPI, HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from config import settings
from logging_config import configure_logging
from models import AssetBase, HoldingBase, InvestmentThesisBase, PerformanceHistoryBase, PortfolioBase
from repositories import FamilyPortfolioRepository
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
portfolio_repository = FamilyPortfolioRepository()


@app.get("/health")
async def health():
    return {"status": "ok", "service": "ai-service"}


@app.get("/api/family-portfolio/portfolios")
async def list_family_portfolios():
    try:
        portfolios = portfolio_repository.list_portfolios()
        return {"items": [portfolio.model_dump(mode="json") for portfolio in portfolios]}
    except Exception as exc:
        logger.exception("list family portfolios failed")
        raise HTTPException(status_code=500, detail=f"读取投资组合失败: {str(exc)}") from exc


@app.post("/api/family-portfolio/portfolios")
async def create_family_portfolio(payload: PortfolioBase):
    try:
        portfolio = portfolio_repository.create_portfolio(payload)
        return portfolio.model_dump(mode="json")
    except Exception as exc:
        logger.exception("create family portfolio failed", payload=payload.model_dump(mode="json"))
        raise HTTPException(status_code=500, detail=f"创建投资组合失败: {str(exc)}") from exc


@app.get("/api/family-portfolio/assets")
async def list_family_assets():
    try:
        assets = portfolio_repository.list_assets()
        return {"items": [asset.model_dump(mode="json") for asset in assets]}
    except Exception as exc:
        logger.exception("list family assets failed")
        raise HTTPException(status_code=500, detail=f"读取资产失败: {str(exc)}") from exc


@app.post("/api/family-portfolio/assets")
async def create_family_asset(payload: AssetBase):
    try:
        asset = portfolio_repository.create_asset(payload)
        return asset.model_dump(mode="json")
    except Exception as exc:
        logger.exception("create family asset failed", payload=payload.model_dump(mode="json"))
        raise HTTPException(status_code=500, detail=f"创建资产失败: {str(exc)}") from exc


@app.post("/api/family-portfolio/holdings")
async def create_family_holding(payload: HoldingBase):
    try:
        holding = portfolio_repository.create_holding(payload)
        return holding.model_dump(mode="json")
    except Exception as exc:
        logger.exception("create family holding failed", payload=payload.model_dump(mode="json"))
        raise HTTPException(status_code=500, detail=f"创建持仓失败: {str(exc)}") from exc


@app.post("/api/family-portfolio/investment-theses")
async def create_family_investment_thesis(payload: InvestmentThesisBase):
    try:
        thesis = portfolio_repository.create_investment_thesis(payload)
        return thesis.model_dump(mode="json")
    except Exception as exc:
        logger.exception("create investment thesis failed", payload=payload.model_dump(mode="json"))
        raise HTTPException(status_code=500, detail=f"创建投资逻辑失败: {str(exc)}") from exc


@app.post("/api/family-portfolio/performance-history")
async def create_family_performance_history(payload: PerformanceHistoryBase):
    try:
        history = portfolio_repository.create_performance_history(payload)
        return history.model_dump(mode="json")
    except Exception as exc:
        logger.exception("create performance history failed", payload=payload.model_dump(mode="json"))
        raise HTTPException(status_code=500, detail=f"创建业绩记录失败: {str(exc)}") from exc


@app.get("/api/family-portfolio/portfolios/{portfolio_id}")
async def get_family_portfolio_aggregate(portfolio_id: int):
    try:
        aggregate = portfolio_repository.get_portfolio_aggregate(portfolio_id)
        if aggregate is None:
            raise HTTPException(status_code=404, detail="投资组合不存在")
        return aggregate.model_dump(mode="json")
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("get family portfolio aggregate failed", portfolio_id=portfolio_id)
        raise HTTPException(status_code=500, detail=f"读取投资组合详情失败: {str(exc)}") from exc


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
async def valuation_backtest(
    symbol: str,
    start_date: str | None = None,
    end_date: str | None = None,
    valuation_mode: str | None = None,
    equity_bond_spread: float | None = None,
    manual_reasonable_pe: float | None = None,
):
    try:
        data = valuation_service.get_backtest(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            valuation_mode=valuation_mode,
            equity_bond_spread=equity_bond_spread,
            manual_reasonable_pe=manual_reasonable_pe,
        )
        return {
            "symbol": symbol,
            "start_date": start_date,
            "end_date": end_date,
            "valuation_mode": valuation_mode,
            "equity_bond_spread": equity_bond_spread,
            "manual_reasonable_pe": manual_reasonable_pe,
            "data": data,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception(
            "valuation backtest failed",
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            valuation_mode=valuation_mode,
            equity_bond_spread=equity_bond_spread,
            manual_reasonable_pe=manual_reasonable_pe,
        )
        raise HTTPException(status_code=500, detail=f"估值回测失败: {str(exc)}") from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
