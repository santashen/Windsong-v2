from __future__ import annotations

import asyncio

import structlog

from config import settings
from services.family_portfolio_market_sync import FamilyPortfolioMarketSyncService


logger = structlog.get_logger()


class FamilyPortfolioScheduler:
    def __init__(self, sync_service: FamilyPortfolioMarketSyncService | None = None) -> None:
        self.sync_service = sync_service or FamilyPortfolioMarketSyncService()
        self._task: asyncio.Task | None = None
        self._stop_event = asyncio.Event()

    async def start(self) -> None:
        if not settings.FAMILY_PORTFOLIO_SYNC_ENABLED or self._task:
            return
        self._stop_event.clear()
        self._task = asyncio.create_task(self._run_loop(), name="family-portfolio-nightly-sync")
        logger.info(
            "family portfolio scheduler started",
            hour=settings.FAMILY_PORTFOLIO_SYNC_HOUR,
            minute=settings.FAMILY_PORTFOLIO_SYNC_MINUTE,
            timezone=settings.FAMILY_PORTFOLIO_SYNC_TIMEZONE,
        )

    async def stop(self) -> None:
        if not self._task:
            return
        self._stop_event.set()
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass
        self._task = None
        logger.info("family portfolio scheduler stopped")

    async def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            wait_seconds = self.sync_service.seconds_until_next_run()
            try:
                await asyncio.wait_for(self._stop_event.wait(), timeout=wait_seconds)
                return
            except asyncio.TimeoutError:
                pass

            try:
                result = await asyncio.to_thread(self.sync_service.sync_all_portfolios)
                logger.info("family portfolio nightly sync completed", result=result)
            except Exception:
                logger.exception("family portfolio nightly sync failed")
