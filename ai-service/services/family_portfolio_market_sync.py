from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time as dt_time, timedelta
from decimal import Decimal, ROUND_HALF_UP
from zoneinfo import ZoneInfo

import structlog

from config import settings
from models import PerformanceHistoryBase
from repositories import FamilyPortfolioRepository
from services.akshare_data import AkshareDataService


logger = structlog.get_logger()
DECIMAL_FOUR_PLACES = Decimal("0.0001")


@dataclass
class AssetSyncResult:
    asset_id: int
    ticker_code: str
    success: bool
    quote_date: date | None = None
    current_price: Decimal | None = None
    error: str | None = None


class FamilyPortfolioMarketSyncService:
    def __init__(
        self,
        repository: FamilyPortfolioRepository | None = None,
        akshare_service: AkshareDataService | None = None,
    ) -> None:
        self.repository = repository or FamilyPortfolioRepository()
        self.akshare_service = akshare_service or AkshareDataService()

    def sync_all_portfolios(self) -> dict:
        return self.sync_all_portfolios_with_logging(run_type="scheduled", triggered_by="scheduler")

    def sync_all_portfolios_with_logging(self, *, run_type: str, triggered_by: str | None) -> dict:
        sync_log = self.repository.create_market_sync_log(
            run_type=run_type,
            status="running",
            triggered_by=triggered_by,
        )
        try:
            result = self._sync_all_portfolios_internal()
            asset_updates = result["asset_updates"]
            portfolio_updates = result["portfolio_updates"]
            completed_log = self.repository.update_market_sync_log(
                sync_log.id,
                status="success",
                asset_update_count=len(asset_updates),
                asset_success_count=sum(1 for item in asset_updates if item["success"]),
                portfolio_update_count=len(portfolio_updates),
                portfolio_success_count=sum(1 for item in portfolio_updates if item["success"]),
                details_json=result,
            )
            result["sync_log"] = completed_log.model_dump(mode="json") if completed_log else None
            return result
        except Exception as exc:
            failed_log = self.repository.update_market_sync_log(
                sync_log.id,
                status="failed",
                asset_update_count=0,
                asset_success_count=0,
                portfolio_update_count=0,
                portfolio_success_count=0,
                details_json=None,
                error_message=str(exc),
            )
            logger.exception("family portfolio sync run failed", sync_log_id=sync_log.id)
            raise

    def list_recent_sync_logs(self, limit: int = 20) -> dict:
        logs = self.repository.list_market_sync_logs(limit=limit)
        return {"items": [item.model_dump(mode="json") for item in logs]}

    def _sync_all_portfolios_internal(self) -> dict:
        assets = self.repository.list_assets()
        asset_results = [self._sync_asset_price(asset) for asset in assets]
        portfolios = self.repository.list_portfolios()
        portfolio_results = []
        for portfolio in portfolios:
            try:
                sync_result = self.sync_portfolio_snapshot(portfolio.id, asset_results)
                portfolio_results.append(sync_result)
            except Exception as exc:
                logger.exception("family portfolio snapshot sync failed", portfolio_id=portfolio.id)
                portfolio_results.append(
                    {
                        "portfolio_id": portfolio.id,
                        "portfolio_name": portfolio.name,
                        "success": False,
                        "error": str(exc),
                    }
                )

        return {
            "asset_updates": [self._serialize_asset_result(item) for item in asset_results],
            "portfolio_updates": portfolio_results,
        }

    def sync_portfolio_snapshot(
        self,
        portfolio_id: int,
        asset_results: list[AssetSyncResult] | None = None,
    ) -> dict:
        aggregate = self.repository.get_portfolio_aggregate(portfolio_id)
        if aggregate is None:
            raise ValueError(f"投资组合 {portfolio_id} 不存在")

        held_asset_ids = {item.asset.id for item in aggregate.holdings}
        quote_dates = [
            item.quote_date
            for item in (asset_results or [])
            if item.success and item.quote_date and item.asset_id in held_asset_ids
        ]
        snapshot_date = min(quote_dates) if quote_dates else self._today_in_timezone()

        total_market_value = Decimal("0")
        for item in aggregate.holdings:
            current_price = item.asset.current_price or Decimal("0")
            total_market_value += item.holding.share_count * current_price

        principal = aggregate.portfolio.total_principal
        portfolio_nav = self._quantize(total_market_value / principal) if principal > 0 else Decimal("0")

        history_records = self.repository.list_performance_history(portfolio_id)
        benchmark_nav_map = self._build_benchmark_nav_map(history_records, snapshot_date)
        benchmark_nav = benchmark_nav_map[snapshot_date]

        performance_record = self.repository.create_performance_history(
            PerformanceHistoryBase(
                portfolio_id=portfolio_id,
                record_date=snapshot_date,
                portfolio_nav=portfolio_nav,
                benchmark_nav=benchmark_nav,
            )
        )

        self._refresh_existing_benchmark_history(history_records, benchmark_nav_map)

        total_return_value = total_market_value - principal
        total_return_rate = (
            self._quantize((total_return_value / principal) * Decimal("100")) if principal > 0 else Decimal("0")
        )

        return {
            "portfolio_id": portfolio_id,
            "portfolio_name": aggregate.portfolio.name,
            "success": True,
            "record_date": snapshot_date.isoformat(),
            "portfolio_nav": str(performance_record.portfolio_nav),
            "benchmark_nav": str(performance_record.benchmark_nav),
            "total_market_value": str(self._quantize(total_market_value)),
            "total_return_value": str(self._quantize(total_return_value)),
            "total_return_rate": str(total_return_rate),
        }

    def seconds_until_next_run(self, now: datetime | None = None) -> float:
        timezone = ZoneInfo(settings.FAMILY_PORTFOLIO_SYNC_TIMEZONE)
        current = now.astimezone(timezone) if now else datetime.now(timezone)
        next_run = datetime.combine(
            current.date(),
            dt_time(hour=settings.FAMILY_PORTFOLIO_SYNC_HOUR, minute=settings.FAMILY_PORTFOLIO_SYNC_MINUTE),
            timezone,
        )
        if current >= next_run:
            next_run = next_run + timedelta(days=1)
        return max((next_run - current).total_seconds(), 1.0)

    def _sync_asset_price(self, asset) -> AssetSyncResult:
        try:
            quote_date, latest_price = self.akshare_service.get_latest_asset_price(
                asset.ticker_code,
                asset.asset_type,
            )
            current_price = self._quantize(Decimal(str(latest_price)))
            self.repository.update_asset_current_price(asset.id, float(current_price))
            return AssetSyncResult(
                asset_id=asset.id,
                ticker_code=asset.ticker_code,
                success=True,
                quote_date=quote_date,
                current_price=current_price,
            )
        except Exception as exc:
            logger.exception(
                "family portfolio asset price sync failed",
                asset_id=asset.id,
                ticker_code=asset.ticker_code,
                asset_type=asset.asset_type,
            )
            return AssetSyncResult(
                asset_id=asset.id,
                ticker_code=asset.ticker_code,
                success=False,
                error=str(exc),
            )

    def _build_benchmark_nav_map(
        self,
        history_records: list,
        snapshot_date: date,
    ) -> dict[date, Decimal]:
        all_dates = sorted({record.record_date for record in history_records} | {snapshot_date})
        index_history = self.akshare_service.get_index_history(
            symbol=settings.FAMILY_PORTFOLIO_BENCHMARK_SYMBOL,
            start_date=all_dates[0] - timedelta(days=30),
            end_date=snapshot_date,
        )
        if index_history.empty:
            raise ValueError("未获取到沪深300历史数据")

        close_by_date: dict[date, Decimal] = {}
        for target_date in all_dates:
            eligible = index_history.loc[index_history["date"].dt.date <= target_date]
            if eligible.empty:
                raise ValueError(f"沪深300缺少 {target_date} 之前的可用收盘价")
            close_by_date[target_date] = Decimal(str(float(eligible.iloc[-1]["close"])))

        baseline_close = close_by_date[all_dates[0]]
        if baseline_close <= 0:
            raise ValueError("沪深300基准起点收盘价无效")

        return {
            target_date: self._quantize(close_value / baseline_close)
            for target_date, close_value in close_by_date.items()
        }

    def _refresh_existing_benchmark_history(self, history_records: list, benchmark_nav_map: dict[date, Decimal]) -> None:
        for record in history_records:
            recalculated_nav = benchmark_nav_map.get(record.record_date)
            if recalculated_nav is None or record.benchmark_nav == recalculated_nav:
                continue
            self.repository.update_performance_history(
                record.id,
                PerformanceHistoryBase(
                    portfolio_id=record.portfolio_id,
                    record_date=record.record_date,
                    portfolio_nav=record.portfolio_nav,
                    benchmark_nav=recalculated_nav,
                ),
            )

    def _serialize_asset_result(self, item: AssetSyncResult) -> dict:
        return {
            "asset_id": item.asset_id,
            "ticker_code": item.ticker_code,
            "success": item.success,
            "quote_date": item.quote_date.isoformat() if item.quote_date else None,
            "current_price": str(item.current_price) if item.current_price is not None else None,
            "error": item.error,
        }

    def _today_in_timezone(self) -> date:
        return datetime.now(ZoneInfo(settings.FAMILY_PORTFOLIO_SYNC_TIMEZONE)).date()

    def _quantize(self, value: Decimal) -> Decimal:
        return value.quantize(DECIMAL_FOUR_PLACES, rounding=ROUND_HALF_UP)
