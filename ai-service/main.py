import time
import uuid

import structlog
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from auth import verify_admin_api_key
from config import settings
from logging_config import configure_logging
from models import AssetBase, HoldingBase, InvestmentThesisBase, PerformanceHistoryBase, PortfolioBase
from services.base_llm import OpenAICompatibleService
from services.family_portfolio import FamilyPortfolioService
from services.family_portfolio_market_sync import FamilyPortfolioMarketSyncService
from services.family_portfolio_scheduler import FamilyPortfolioScheduler
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
family_portfolio_service = FamilyPortfolioService()
family_portfolio_market_sync_service = FamilyPortfolioMarketSyncService()
family_portfolio_scheduler = FamilyPortfolioScheduler(sync_service=family_portfolio_market_sync_service)


@app.on_event("startup")
async def startup_family_portfolio_scheduler():
    await family_portfolio_scheduler.start()


@app.on_event("shutdown")
async def shutdown_family_portfolio_scheduler():
    await family_portfolio_scheduler.stop()


@app.get("/health")
async def health():
    return {"status": "ok", "service": "ai-service"}


@app.get("/api/family-portfolio/portfolios")
async def list_family_portfolios():
    try:
        return family_portfolio_service.list_portfolios()
    except Exception as exc:
        logger.exception("list family portfolios failed")
        raise HTTPException(status_code=500, detail=f"读取投资组合失败: {str(exc)}") from exc


@app.post("/api/family-portfolio/portfolios")
async def create_family_portfolio(payload: PortfolioBase, _: None = Depends(verify_admin_api_key)):
    try:
        return family_portfolio_service.create_portfolio(payload)
    except Exception as exc:
        logger.exception("create family portfolio failed", payload=payload.model_dump(mode="json"))
        raise HTTPException(status_code=500, detail=f"创建投资组合失败: {str(exc)}") from exc


@app.put("/api/family-portfolio/portfolios/{portfolio_id}")
async def update_family_portfolio(
    portfolio_id: int, payload: PortfolioBase, _: None = Depends(verify_admin_api_key)
):
    try:
        portfolio = family_portfolio_service.update_portfolio(portfolio_id, payload)
        if portfolio is None:
            raise HTTPException(status_code=404, detail="投资组合不存在")
        return portfolio
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(
            "update family portfolio failed",
            portfolio_id=portfolio_id,
            payload=payload.model_dump(mode="json"),
        )
        raise HTTPException(status_code=500, detail=f"更新投资组合失败: {str(exc)}") from exc


@app.delete("/api/family-portfolio/portfolios/{portfolio_id}")
async def delete_family_portfolio(portfolio_id: int, _: None = Depends(verify_admin_api_key)):
    try:
        deleted = family_portfolio_service.delete_portfolio(portfolio_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="投资组合不存在")
        return {"deleted": True, "portfolio_id": portfolio_id}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("delete family portfolio failed", portfolio_id=portfolio_id)
        raise HTTPException(status_code=500, detail=f"删除投资组合失败: {str(exc)}") from exc


@app.get("/api/family-portfolio/assets")
async def list_family_assets():
    try:
        return family_portfolio_service.list_assets()
    except Exception as exc:
        logger.exception("list family assets failed")
        raise HTTPException(status_code=500, detail=f"读取资产失败: {str(exc)}") from exc


@app.post("/api/family-portfolio/assets")
async def create_family_asset(payload: AssetBase, _: None = Depends(verify_admin_api_key)):
    try:
        return family_portfolio_service.create_asset(payload)
    except Exception as exc:
        logger.exception("create family asset failed", payload=payload.model_dump(mode="json"))
        raise HTTPException(status_code=500, detail=f"创建资产失败: {str(exc)}") from exc


@app.put("/api/family-portfolio/assets/{asset_id}")
async def update_family_asset(
    asset_id: int, payload: AssetBase, _: None = Depends(verify_admin_api_key)
):
    try:
        asset = family_portfolio_service.update_asset(asset_id, payload)
        if asset is None:
            raise HTTPException(status_code=404, detail="资产不存在")
        return asset
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("update family asset failed", asset_id=asset_id, payload=payload.model_dump(mode="json"))
        raise HTTPException(status_code=500, detail=f"更新资产失败: {str(exc)}") from exc


@app.delete("/api/family-portfolio/assets/{asset_id}")
async def delete_family_asset(asset_id: int, _: None = Depends(verify_admin_api_key)):
    try:
        deleted = family_portfolio_service.delete_asset(asset_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="资产不存在")
        return {"deleted": True, "asset_id": asset_id}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("delete family asset failed", asset_id=asset_id)
        raise HTTPException(status_code=500, detail=f"删除资产失败: {str(exc)}") from exc


@app.post("/api/family-portfolio/holdings")
async def create_family_holding(payload: HoldingBase, _: None = Depends(verify_admin_api_key)):
    try:
        return family_portfolio_service.create_holding(payload)
    except Exception as exc:
        logger.exception("create family holding failed", payload=payload.model_dump(mode="json"))
        raise HTTPException(status_code=500, detail=f"创建持仓失败: {str(exc)}") from exc


@app.put("/api/family-portfolio/holdings/{holding_id}")
async def update_family_holding(
    holding_id: int, payload: HoldingBase, _: None = Depends(verify_admin_api_key)
):
    try:
        holding = family_portfolio_service.update_holding(holding_id, payload)
        if holding is None:
            raise HTTPException(status_code=404, detail="持仓不存在")
        return holding
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("update family holding failed", holding_id=holding_id, payload=payload.model_dump(mode="json"))
        raise HTTPException(status_code=500, detail=f"更新持仓失败: {str(exc)}") from exc


@app.delete("/api/family-portfolio/holdings/{holding_id}")
async def delete_family_holding(holding_id: int, _: None = Depends(verify_admin_api_key)):
    try:
        deleted = family_portfolio_service.delete_holding(holding_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="持仓不存在")
        return {"deleted": True, "holding_id": holding_id}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("delete family holding failed", holding_id=holding_id)
        raise HTTPException(status_code=500, detail=f"删除持仓失败: {str(exc)}") from exc


@app.post("/api/family-portfolio/sync/market")
async def sync_family_portfolio_market(_: None = Depends(verify_admin_api_key)):
    try:
        return family_portfolio_market_sync_service.sync_all_portfolios_with_logging(
            run_type="manual",
            triggered_by="admin_api",
        )
    except Exception as exc:
        logger.exception("sync family portfolio market failed")
        raise HTTPException(status_code=500, detail=f"同步家庭投资组合行情失败: {str(exc)}") from exc


@app.get("/api/family-portfolio/sync/logs")
async def list_family_portfolio_sync_logs(_: None = Depends(verify_admin_api_key)):
    try:
        return family_portfolio_market_sync_service.list_recent_sync_logs()
    except Exception as exc:
        logger.exception("list family portfolio sync logs failed")
        raise HTTPException(status_code=500, detail=f"读取同步日志失败: {str(exc)}") from exc


@app.post("/api/family-portfolio/investment-theses")
async def create_family_investment_thesis(
    payload: InvestmentThesisBase, _: None = Depends(verify_admin_api_key)
):
    try:
        return family_portfolio_service.create_investment_thesis(payload)
    except Exception as exc:
        logger.exception("create investment thesis failed", payload=payload.model_dump(mode="json"))
        raise HTTPException(status_code=500, detail=f"创建投资逻辑失败: {str(exc)}") from exc


@app.put("/api/family-portfolio/investment-theses/{thesis_id}")
async def update_family_investment_thesis(
    thesis_id: int, payload: InvestmentThesisBase, _: None = Depends(verify_admin_api_key)
):
    try:
        thesis = family_portfolio_service.update_investment_thesis(thesis_id, payload)
        if thesis is None:
            raise HTTPException(status_code=404, detail="投资逻辑不存在")
        return thesis
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(
            "update investment thesis failed",
            thesis_id=thesis_id,
            payload=payload.model_dump(mode="json"),
        )
        raise HTTPException(status_code=500, detail=f"更新投资逻辑失败: {str(exc)}") from exc


@app.delete("/api/family-portfolio/investment-theses/{thesis_id}")
async def delete_family_investment_thesis(thesis_id: int, _: None = Depends(verify_admin_api_key)):
    try:
        deleted = family_portfolio_service.delete_investment_thesis(thesis_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="投资逻辑不存在")
        return {"deleted": True, "thesis_id": thesis_id}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("delete investment thesis failed", thesis_id=thesis_id)
        raise HTTPException(status_code=500, detail=f"删除投资逻辑失败: {str(exc)}") from exc


@app.post("/api/family-portfolio/performance-history")
async def create_family_performance_history(
    payload: PerformanceHistoryBase, _: None = Depends(verify_admin_api_key)
):
    try:
        return family_portfolio_service.create_performance_history(payload)
    except Exception as exc:
        logger.exception("create performance history failed", payload=payload.model_dump(mode="json"))
        raise HTTPException(status_code=500, detail=f"创建业绩记录失败: {str(exc)}") from exc


@app.put("/api/family-portfolio/performance-history/{history_id}")
async def update_family_performance_history(
    history_id: int, payload: PerformanceHistoryBase, _: None = Depends(verify_admin_api_key)
):
    try:
        history = family_portfolio_service.update_performance_history(history_id, payload)
        if history is None:
            raise HTTPException(status_code=404, detail="业绩记录不存在")
        return history
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(
            "update performance history failed",
            history_id=history_id,
            payload=payload.model_dump(mode="json"),
        )
        raise HTTPException(status_code=500, detail=f"更新业绩记录失败: {str(exc)}") from exc


@app.delete("/api/family-portfolio/performance-history/{history_id}")
async def delete_family_performance_history(
    history_id: int, _: None = Depends(verify_admin_api_key)
):
    try:
        deleted = family_portfolio_service.delete_performance_history(history_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="业绩记录不存在")
        return {"deleted": True, "history_id": history_id}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("delete performance history failed", history_id=history_id)
        raise HTTPException(status_code=500, detail=f"删除业绩记录失败: {str(exc)}") from exc


@app.get("/api/family-portfolio/portfolios/{portfolio_id}")
async def get_family_portfolio_aggregate(portfolio_id: int):
    try:
        aggregate = family_portfolio_service.get_portfolio_detail(portfolio_id)
        if aggregate is None:
            raise HTTPException(status_code=404, detail="投资组合不存在")
        return aggregate
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
