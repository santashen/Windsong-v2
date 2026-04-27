from __future__ import annotations

from typing import Any

from database import get_db_connection
from psycopg.types.json import Jsonb
from models import (
    AssetBase,
    AssetRecord,
    HoldingBase,
    HoldingRecord,
    InvestmentThesisBase,
    InvestmentThesisRecord,
    MarketSyncLogRecord,
    PerformanceHistoryBase,
    PerformanceHistoryRecord,
    PortfolioAggregateView,
    PortfolioBase,
    PortfolioHoldingView,
    PortfolioRecord,
)


class FamilyPortfolioRepository:
    def create_market_sync_log(
        self,
        *,
        run_type: str,
        status: str,
        triggered_by: str | None,
        asset_update_count: int = 0,
        asset_success_count: int = 0,
        portfolio_update_count: int = 0,
        portfolio_success_count: int = 0,
        details_json: dict[str, Any] | None = None,
        error_message: str | None = None,
    ) -> MarketSyncLogRecord:
        query = """
            INSERT INTO family_portfolio_market_sync_logs (
                run_type,
                status,
                triggered_by,
                asset_update_count,
                asset_success_count,
                portfolio_update_count,
                portfolio_success_count,
                details_json,
                error_message
            )
            VALUES (
                %(run_type)s,
                %(status)s,
                %(triggered_by)s,
                %(asset_update_count)s,
                %(asset_success_count)s,
                %(portfolio_update_count)s,
                %(portfolio_success_count)s,
                %(details_json)s,
                %(error_message)s
            )
            RETURNING id, run_type, status, triggered_by, asset_update_count, asset_success_count,
                      portfolio_update_count, portfolio_success_count, details_json, error_message,
                      started_at, finished_at, created_at, updated_at
        """
        payload = {
            "run_type": run_type,
            "status": status,
            "triggered_by": triggered_by,
            "asset_update_count": asset_update_count,
            "asset_success_count": asset_success_count,
            "portfolio_update_count": portfolio_update_count,
            "portfolio_success_count": portfolio_success_count,
            "details_json": Jsonb(details_json) if details_json is not None else None,
            "error_message": error_message,
        }
        with get_db_connection() as connection, connection.cursor() as cursor:
            cursor.execute(query, payload)
            row = cursor.fetchone()
        return MarketSyncLogRecord.model_validate(row)

    def update_market_sync_log(
        self,
        log_id: int,
        *,
        status: str,
        asset_update_count: int,
        asset_success_count: int,
        portfolio_update_count: int,
        portfolio_success_count: int,
        details_json: dict[str, Any] | None,
        error_message: str | None = None,
    ) -> MarketSyncLogRecord | None:
        query = """
            UPDATE family_portfolio_market_sync_logs
            SET
                status = %(status)s,
                asset_update_count = %(asset_update_count)s,
                asset_success_count = %(asset_success_count)s,
                portfolio_update_count = %(portfolio_update_count)s,
                portfolio_success_count = %(portfolio_success_count)s,
                details_json = %(details_json)s,
                error_message = %(error_message)s,
                finished_at = NOW()
            WHERE id = %(log_id)s
            RETURNING id, run_type, status, triggered_by, asset_update_count, asset_success_count,
                      portfolio_update_count, portfolio_success_count, details_json, error_message,
                      started_at, finished_at, created_at, updated_at
        """
        payload = {
            "log_id": log_id,
            "status": status,
            "asset_update_count": asset_update_count,
            "asset_success_count": asset_success_count,
            "portfolio_update_count": portfolio_update_count,
            "portfolio_success_count": portfolio_success_count,
            "details_json": Jsonb(details_json) if details_json is not None else None,
            "error_message": error_message,
        }
        with get_db_connection() as connection, connection.cursor() as cursor:
            cursor.execute(query, payload)
            row = cursor.fetchone()
        return MarketSyncLogRecord.model_validate(row) if row else None

    def list_market_sync_logs(self, limit: int = 20) -> list[MarketSyncLogRecord]:
        query = """
            SELECT id, run_type, status, triggered_by, asset_update_count, asset_success_count,
                   portfolio_update_count, portfolio_success_count, details_json, error_message,
                   started_at, finished_at, created_at, updated_at
            FROM family_portfolio_market_sync_logs
            ORDER BY started_at DESC, id DESC
            LIMIT %(limit)s
        """
        with get_db_connection(autocommit=True) as connection, connection.cursor() as cursor:
            cursor.execute(query, {"limit": limit})
            rows = cursor.fetchall()
        return [MarketSyncLogRecord.model_validate(row) for row in rows]

    def create_portfolio(self, portfolio: PortfolioBase) -> PortfolioRecord:
        query = """
            INSERT INTO portfolios (name, total_principal, currency)
            VALUES (%(name)s, %(total_principal)s, %(currency)s)
            RETURNING id, name, total_principal, currency, created_at, updated_at
        """
        with get_db_connection() as connection, connection.cursor() as cursor:
            cursor.execute(query, portfolio.model_dump())
            row = cursor.fetchone()
        return PortfolioRecord.model_validate(row)

    def list_portfolios(self) -> list[PortfolioRecord]:
        query = """
            SELECT id, name, total_principal, currency, created_at, updated_at
            FROM portfolios
            ORDER BY id
        """
        with get_db_connection(autocommit=True) as connection, connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
        return [PortfolioRecord.model_validate(row) for row in rows]

    def get_portfolio_by_id(self, portfolio_id: int) -> PortfolioRecord | None:
        query = """
            SELECT id, name, total_principal, currency, created_at, updated_at
            FROM portfolios
            WHERE id = %(portfolio_id)s
        """
        with get_db_connection(autocommit=True) as connection, connection.cursor() as cursor:
            cursor.execute(query, {"portfolio_id": portfolio_id})
            row = cursor.fetchone()
        return PortfolioRecord.model_validate(row) if row else None

    def update_portfolio(self, portfolio_id: int, portfolio: PortfolioBase) -> PortfolioRecord | None:
        query = """
            UPDATE portfolios
            SET
                name = %(name)s,
                total_principal = %(total_principal)s,
                currency = %(currency)s
            WHERE id = %(portfolio_id)s
            RETURNING id, name, total_principal, currency, created_at, updated_at
        """
        payload = {"portfolio_id": portfolio_id, **portfolio.model_dump()}
        with get_db_connection() as connection, connection.cursor() as cursor:
            cursor.execute(query, payload)
            row = cursor.fetchone()
        return PortfolioRecord.model_validate(row) if row else None

    def delete_portfolio(self, portfolio_id: int) -> bool:
        query = """
            DELETE FROM portfolios
            WHERE id = %(portfolio_id)s
        """
        with get_db_connection() as connection, connection.cursor() as cursor:
            cursor.execute(query, {"portfolio_id": portfolio_id})
            deleted = cursor.rowcount > 0
        return deleted

    def create_asset(self, asset: AssetBase) -> AssetRecord:
        query = """
            INSERT INTO assets (ticker_code, name, sector, asset_type, icon_name, current_price)
            VALUES (
                %(ticker_code)s,
                %(name)s,
                %(sector)s,
                %(asset_type)s,
                %(icon_name)s,
                %(current_price)s
            )
            ON CONFLICT (ticker_code) DO UPDATE
            SET
                name = EXCLUDED.name,
                sector = EXCLUDED.sector,
                asset_type = EXCLUDED.asset_type,
                icon_name = EXCLUDED.icon_name,
                current_price = EXCLUDED.current_price
            RETURNING id, ticker_code, name, sector, asset_type, icon_name, current_price, created_at, updated_at
        """
        payload = asset.model_dump(mode="json")
        with get_db_connection() as connection, connection.cursor() as cursor:
            cursor.execute(query, payload)
            row = cursor.fetchone()
        return AssetRecord.model_validate(row)

    def list_assets(self) -> list[AssetRecord]:
        query = """
            SELECT id, ticker_code, name, sector, asset_type, icon_name, current_price, created_at, updated_at
            FROM assets
            ORDER BY id
        """
        with get_db_connection(autocommit=True) as connection, connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
        return [AssetRecord.model_validate(row) for row in rows]

    def get_asset_by_id(self, asset_id: int) -> AssetRecord | None:
        query = """
            SELECT id, ticker_code, name, sector, asset_type, icon_name, current_price, created_at, updated_at
            FROM assets
            WHERE id = %(asset_id)s
        """
        with get_db_connection(autocommit=True) as connection, connection.cursor() as cursor:
            cursor.execute(query, {"asset_id": asset_id})
            row = cursor.fetchone()
        return AssetRecord.model_validate(row) if row else None

    def update_asset(self, asset_id: int, asset: AssetBase) -> AssetRecord | None:
        query = """
            UPDATE assets
            SET
                ticker_code = %(ticker_code)s,
                name = %(name)s,
                sector = %(sector)s,
                asset_type = %(asset_type)s,
                icon_name = %(icon_name)s,
                current_price = %(current_price)s
            WHERE id = %(asset_id)s
            RETURNING id, ticker_code, name, sector, asset_type, icon_name, current_price, created_at, updated_at
        """
        payload = {"asset_id": asset_id, **asset.model_dump(mode="json")}
        with get_db_connection() as connection, connection.cursor() as cursor:
            cursor.execute(query, payload)
            row = cursor.fetchone()
        return AssetRecord.model_validate(row) if row else None

    def update_asset_current_price(self, asset_id: int, current_price: float) -> AssetRecord | None:
        query = """
            UPDATE assets
            SET current_price = %(current_price)s
            WHERE id = %(asset_id)s
            RETURNING id, ticker_code, name, sector, asset_type, icon_name, current_price, created_at, updated_at
        """
        with get_db_connection() as connection, connection.cursor() as cursor:
            cursor.execute(query, {"asset_id": asset_id, "current_price": current_price})
            row = cursor.fetchone()
        return AssetRecord.model_validate(row) if row else None

    def delete_asset(self, asset_id: int) -> bool:
        query = """
            DELETE FROM assets
            WHERE id = %(asset_id)s
        """
        with get_db_connection() as connection, connection.cursor() as cursor:
            cursor.execute(query, {"asset_id": asset_id})
            deleted = cursor.rowcount > 0
        return deleted

    def create_holding(self, holding: HoldingBase) -> HoldingRecord:
        query = """
            INSERT INTO holdings (
                portfolio_id,
                asset_id,
                invested_amount,
                share_count,
                average_cost,
                weight_percentage
            )
            VALUES (
                %(portfolio_id)s,
                %(asset_id)s,
                %(invested_amount)s,
                %(share_count)s,
                CASE
                    WHEN %(share_count)s > 0
                    THEN ROUND((%(invested_amount)s / %(share_count)s)::numeric, 4)
                    ELSE 0
                END,
                %(weight_percentage)s
            )
            ON CONFLICT (portfolio_id, asset_id) DO UPDATE
            SET
                invested_amount = EXCLUDED.invested_amount,
                share_count = EXCLUDED.share_count,
                average_cost = CASE
                    WHEN EXCLUDED.share_count > 0
                    THEN ROUND((EXCLUDED.invested_amount / EXCLUDED.share_count)::numeric, 4)
                    ELSE 0
                END,
                weight_percentage = EXCLUDED.weight_percentage
            RETURNING id, portfolio_id, asset_id, invested_amount, share_count, average_cost, weight_percentage, created_at, updated_at
        """
        with get_db_connection() as connection, connection.cursor() as cursor:
            cursor.execute(query, holding.model_dump())
            row = cursor.fetchone()
        return HoldingRecord.model_validate(row)

    def update_holding(self, holding_id: int, holding: HoldingBase) -> HoldingRecord | None:
        query = """
            UPDATE holdings
            SET
                portfolio_id = %(portfolio_id)s,
                asset_id = %(asset_id)s,
                invested_amount = %(invested_amount)s,
                share_count = %(share_count)s,
                average_cost = CASE
                    WHEN %(share_count)s > 0
                    THEN ROUND((%(invested_amount)s / %(share_count)s)::numeric, 4)
                    ELSE 0
                END,
                weight_percentage = %(weight_percentage)s
            WHERE id = %(holding_id)s
            RETURNING id, portfolio_id, asset_id, invested_amount, share_count, average_cost, weight_percentage, created_at, updated_at
        """
        payload = {"holding_id": holding_id, **holding.model_dump()}
        with get_db_connection() as connection, connection.cursor() as cursor:
            cursor.execute(query, payload)
            row = cursor.fetchone()
        return HoldingRecord.model_validate(row) if row else None

    def delete_holding(self, holding_id: int) -> bool:
        query = """
            DELETE FROM holdings
            WHERE id = %(holding_id)s
        """
        with get_db_connection() as connection, connection.cursor() as cursor:
            cursor.execute(query, {"holding_id": holding_id})
            deleted = cursor.rowcount > 0
        return deleted

    def create_investment_thesis(self, thesis: InvestmentThesisBase) -> InvestmentThesisRecord:
        query = """
            INSERT INTO investment_theses (
                asset_id,
                strategy_tag,
                expected_dividend_yield,
                margin_of_safety,
                valuation_metric_name,
                percentile_value,
                short_description,
                markdown_details
            )
            VALUES (
                %(asset_id)s,
                %(strategy_tag)s,
                %(expected_dividend_yield)s,
                %(margin_of_safety)s,
                %(valuation_metric_name)s,
                %(percentile_value)s,
                %(short_description)s,
                %(markdown_details)s
            )
            RETURNING
                id,
                asset_id,
                strategy_tag,
                expected_dividend_yield,
                margin_of_safety,
                valuation_metric_name,
                percentile_value,
                short_description,
                markdown_details,
                created_at,
                updated_at
        """
        with get_db_connection() as connection, connection.cursor() as cursor:
            cursor.execute(query, thesis.model_dump())
            row = cursor.fetchone()
        return InvestmentThesisRecord.model_validate(row)

    def update_investment_thesis(
        self, thesis_id: int, thesis: InvestmentThesisBase
    ) -> InvestmentThesisRecord | None:
        query = """
            UPDATE investment_theses
            SET
                asset_id = %(asset_id)s,
                strategy_tag = %(strategy_tag)s,
                expected_dividend_yield = %(expected_dividend_yield)s,
                margin_of_safety = %(margin_of_safety)s,
                valuation_metric_name = %(valuation_metric_name)s,
                percentile_value = %(percentile_value)s,
                short_description = %(short_description)s,
                markdown_details = %(markdown_details)s
            WHERE id = %(thesis_id)s
            RETURNING
                id,
                asset_id,
                strategy_tag,
                expected_dividend_yield,
                margin_of_safety,
                valuation_metric_name,
                percentile_value,
                short_description,
                markdown_details,
                created_at,
                updated_at
        """
        payload = {"thesis_id": thesis_id, **thesis.model_dump()}
        with get_db_connection() as connection, connection.cursor() as cursor:
            cursor.execute(query, payload)
            row = cursor.fetchone()
        return InvestmentThesisRecord.model_validate(row) if row else None

    def delete_investment_thesis(self, thesis_id: int) -> bool:
        query = """
            DELETE FROM investment_theses
            WHERE id = %(thesis_id)s
        """
        with get_db_connection() as connection, connection.cursor() as cursor:
            cursor.execute(query, {"thesis_id": thesis_id})
            deleted = cursor.rowcount > 0
        return deleted

    def create_performance_history(self, history: PerformanceHistoryBase) -> PerformanceHistoryRecord:
        query = """
            INSERT INTO performance_history (portfolio_id, record_date, portfolio_nav, benchmark_nav)
            VALUES (%(portfolio_id)s, %(record_date)s, %(portfolio_nav)s, %(benchmark_nav)s)
            ON CONFLICT (portfolio_id, record_date) DO UPDATE
            SET
                portfolio_nav = EXCLUDED.portfolio_nav,
                benchmark_nav = EXCLUDED.benchmark_nav
            RETURNING id, portfolio_id, record_date, portfolio_nav, benchmark_nav, created_at, updated_at
        """
        with get_db_connection() as connection, connection.cursor() as cursor:
            cursor.execute(query, history.model_dump())
            row = cursor.fetchone()
        return PerformanceHistoryRecord.model_validate(row)

    def update_performance_history(
        self, history_id: int, history: PerformanceHistoryBase
    ) -> PerformanceHistoryRecord | None:
        query = """
            UPDATE performance_history
            SET
                portfolio_id = %(portfolio_id)s,
                record_date = %(record_date)s,
                portfolio_nav = %(portfolio_nav)s,
                benchmark_nav = %(benchmark_nav)s
            WHERE id = %(history_id)s
            RETURNING id, portfolio_id, record_date, portfolio_nav, benchmark_nav, created_at, updated_at
        """
        payload = {"history_id": history_id, **history.model_dump()}
        with get_db_connection() as connection, connection.cursor() as cursor:
            cursor.execute(query, payload)
            row = cursor.fetchone()
        return PerformanceHistoryRecord.model_validate(row) if row else None

    def list_performance_history(self, portfolio_id: int) -> list[PerformanceHistoryRecord]:
        query = """
            SELECT id, portfolio_id, record_date, portfolio_nav, benchmark_nav, created_at, updated_at
            FROM performance_history
            WHERE portfolio_id = %(portfolio_id)s
            ORDER BY record_date
        """
        with get_db_connection(autocommit=True) as connection, connection.cursor() as cursor:
            cursor.execute(query, {"portfolio_id": portfolio_id})
            rows = cursor.fetchall()
        return [PerformanceHistoryRecord.model_validate(row) for row in rows]

    def delete_performance_history(self, history_id: int) -> bool:
        query = """
            DELETE FROM performance_history
            WHERE id = %(history_id)s
        """
        with get_db_connection() as connection, connection.cursor() as cursor:
            cursor.execute(query, {"history_id": history_id})
            deleted = cursor.rowcount > 0
        return deleted

    def get_portfolio_aggregate(self, portfolio_id: int) -> PortfolioAggregateView | None:
        portfolio_query = """
            SELECT id, name, total_principal, currency, created_at, updated_at
            FROM portfolios
            WHERE id = %(portfolio_id)s
        """
        holdings_query = """
            SELECT
                h.id AS holding_id,
                h.portfolio_id,
                h.asset_id,
                h.invested_amount,
                h.share_count,
                h.average_cost,
                h.weight_percentage,
                h.created_at AS holding_created_at,
                h.updated_at AS holding_updated_at,
                a.id AS asset_record_id,
                a.ticker_code,
                a.name AS asset_name,
                a.sector,
                a.asset_type,
                a.icon_name,
                a.current_price,
                a.created_at AS asset_created_at,
                a.updated_at AS asset_updated_at,
                t.id AS thesis_id,
                t.asset_id AS thesis_asset_id,
                t.strategy_tag,
                t.expected_dividend_yield,
                t.margin_of_safety,
                t.valuation_metric_name,
                t.percentile_value,
                t.short_description,
                t.markdown_details,
                t.created_at AS thesis_created_at,
                t.updated_at AS thesis_updated_at
            FROM holdings h
            JOIN assets a ON a.id = h.asset_id
            LEFT JOIN LATERAL (
                SELECT *
                FROM investment_theses t
                WHERE t.asset_id = a.id
                ORDER BY t.updated_at DESC, t.id DESC
                LIMIT 1
            ) t ON TRUE
            WHERE h.portfolio_id = %(portfolio_id)s
            ORDER BY h.weight_percentage DESC, h.id
        """
        performance_query = """
            SELECT id, portfolio_id, record_date, portfolio_nav, benchmark_nav, created_at, updated_at
            FROM performance_history
            WHERE portfolio_id = %(portfolio_id)s
            ORDER BY record_date
        """

        with get_db_connection(autocommit=True) as connection, connection.cursor() as cursor:
            cursor.execute(portfolio_query, {"portfolio_id": portfolio_id})
            portfolio_row = cursor.fetchone()
            if not portfolio_row:
                return None

            cursor.execute(holdings_query, {"portfolio_id": portfolio_id})
            holdings_rows = cursor.fetchall()

            cursor.execute(performance_query, {"portfolio_id": portfolio_id})
            performance_rows = cursor.fetchall()

        holdings = [self._build_portfolio_holding_view(row) for row in holdings_rows]
        performance_history = [PerformanceHistoryRecord.model_validate(row) for row in performance_rows]

        return PortfolioAggregateView(
            portfolio=PortfolioRecord.model_validate(portfolio_row),
            holdings=holdings,
            performance_history=performance_history,
        )

    @staticmethod
    def _build_portfolio_holding_view(row: dict[str, Any]) -> PortfolioHoldingView:
        holding = HoldingRecord.model_validate(
            {
                "id": row["holding_id"],
                "portfolio_id": row["portfolio_id"],
                "asset_id": row["asset_id"],
                "invested_amount": row["invested_amount"],
                "share_count": row["share_count"],
                "average_cost": row["average_cost"],
                "weight_percentage": row["weight_percentage"],
                "created_at": row["holding_created_at"],
                "updated_at": row["holding_updated_at"],
            }
        )
        asset = AssetRecord.model_validate(
            {
                "id": row["asset_record_id"],
                "ticker_code": row["ticker_code"],
                "name": row["asset_name"],
                "sector": row["sector"],
                "asset_type": row["asset_type"],
                "icon_name": row["icon_name"],
                "current_price": row["current_price"],
                "created_at": row["asset_created_at"],
                "updated_at": row["asset_updated_at"],
            }
        )
        thesis = None
        if row["thesis_id"] is not None:
            thesis = InvestmentThesisRecord.model_validate(
                {
                    "id": row["thesis_id"],
                    "asset_id": row["thesis_asset_id"],
                    "strategy_tag": row["strategy_tag"],
                    "expected_dividend_yield": row["expected_dividend_yield"],
                    "margin_of_safety": row["margin_of_safety"],
                    "valuation_metric_name": row["valuation_metric_name"],
                    "percentile_value": row["percentile_value"],
                    "short_description": row["short_description"],
                    "markdown_details": row["markdown_details"],
                    "created_at": row["thesis_created_at"],
                    "updated_at": row["thesis_updated_at"],
                }
            )

        return PortfolioHoldingView(holding=holding, asset=asset, investment_thesis=thesis)
