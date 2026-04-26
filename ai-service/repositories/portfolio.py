from __future__ import annotations

from typing import Any

from database import get_db_connection
from models import (
    AssetBase,
    AssetRecord,
    HoldingBase,
    HoldingRecord,
    InvestmentThesisBase,
    InvestmentThesisRecord,
    PerformanceHistoryBase,
    PerformanceHistoryRecord,
    PortfolioAggregateView,
    PortfolioBase,
    PortfolioHoldingView,
    PortfolioRecord,
)


class FamilyPortfolioRepository:
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
                %(average_cost)s,
                %(weight_percentage)s
            )
            ON CONFLICT (portfolio_id, asset_id) DO UPDATE
            SET
                invested_amount = EXCLUDED.invested_amount,
                share_count = EXCLUDED.share_count,
                average_cost = EXCLUDED.average_cost,
                weight_percentage = EXCLUDED.weight_percentage
            RETURNING id, portfolio_id, asset_id, invested_amount, share_count, average_cost, weight_percentage, created_at, updated_at
        """
        with get_db_connection() as connection, connection.cursor() as cursor:
            cursor.execute(query, holding.model_dump())
            row = cursor.fetchone()
        return HoldingRecord.model_validate(row)

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
