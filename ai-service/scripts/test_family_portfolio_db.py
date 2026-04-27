from __future__ import annotations

import json
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from models import (
    AssetBase,
    AssetType,
    HoldingBase,
    InvestmentThesisBase,
    PerformanceHistoryBase,
    PortfolioBase,
)
from repositories import FamilyPortfolioRepository


def main() -> None:
    repository = FamilyPortfolioRepository()

    portfolio = repository.create_portfolio(
        PortfolioBase(
            name="家庭核心配置",
            total_principal=Decimal("1000000.0000"),
            currency="CNY",
        )
    )

    assets = [
        repository.create_asset(
            AssetBase(
                ticker_code="515450.SH",
                name="低波红利50 ETF",
                sector="股票指数基金",
                asset_type=AssetType.ETF,
                icon_name="shield",
                current_price=Decimal("1.1280"),
            )
        ),
        repository.create_asset(
            AssetBase(
                ticker_code="600941.SH",
                name="中国移动",
                sector="电信运营",
                asset_type=AssetType.STOCK,
                icon_name="cell_tower",
                current_price=Decimal("104.1500"),
            )
        ),
        repository.create_asset(
            AssetBase(
                ticker_code="000333.SZ",
                name="美的集团",
                sector="白色家电",
                asset_type=AssetType.STOCK,
                icon_name="precision_manufacturing",
                current_price=Decimal("71.4500"),
            )
        ),
    ]

    repository.create_holding(
        HoldingBase(
            portfolio_id=portfolio.id,
            asset_id=assets[0].id,
            invested_amount=Decimal("250000.0000"),
            share_count=Decimal("221631.2057"),
            average_cost=Decimal("1.1280"),
            weight_percentage=Decimal("25.0000"),
        )
    )
    repository.create_holding(
        HoldingBase(
            portfolio_id=portfolio.id,
            asset_id=assets[1].id,
            invested_amount=Decimal("500000.0000"),
            share_count=Decimal("4800.0000"),
            average_cost=Decimal("104.1667"),
            weight_percentage=Decimal("50.0000"),
        )
    )
    repository.create_holding(
        HoldingBase(
            portfolio_id=portfolio.id,
            asset_id=assets[2].id,
            invested_amount=Decimal("250000.0000"),
            share_count=Decimal("3498.9503"),
            average_cost=Decimal("71.4500"),
            weight_percentage=Decimal("25.0000"),
        )
    )

    repository.create_investment_thesis(
        InvestmentThesisBase(
            asset_id=assets[1].id,
            strategy_tag="垄断护城河",
            expected_dividend_yield=Decimal("7.2000"),
            margin_of_safety=Decimal("35.4000"),
            markdown_details="# 中国移动深度逻辑\n\n### 1. 业务壁垒\n拥有全国最大的5G基站覆盖量...\n\n### 2. 现金流分析\n资本开支高峰期已过，分红比例持续提升...",
        )
    )

    repository.create_performance_history(
        PerformanceHistoryBase(
            portfolio_id=portfolio.id,
            record_date=date(2026, 4, 26),
            portfolio_nav=Decimal("1.1532"),
            benchmark_nav=Decimal("1.0845"),
        )
    )

    aggregate = repository.get_portfolio_aggregate(portfolio.id)
    print(json.dumps(aggregate.model_dump(mode="json"), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
