from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


class AssetType(str, Enum):
    STOCK = "stock"
    ETF = "etf"
    FUND = "fund"
    BOND = "bond"
    CASH = "cash"
    OTHER = "other"


class PortfolioBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    total_principal: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    currency: str = Field(default="CNY", min_length=1, max_length=10)


class PortfolioRecord(PortfolioBase):
    id: int
    created_at: datetime
    updated_at: datetime


class AssetBase(BaseModel):
    ticker_code: str = Field(min_length=1, max_length=20)
    name: str = Field(min_length=1, max_length=100)
    sector: str | None = Field(default=None, max_length=50)
    asset_type: AssetType
    icon_name: str | None = Field(default=None, max_length=50)
    current_price: Decimal | None = Field(default=None, ge=Decimal("0"))


class AssetRecord(AssetBase):
    id: int
    created_at: datetime
    updated_at: datetime


class HoldingBase(BaseModel):
    portfolio_id: int
    asset_id: int
    invested_amount: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    share_count: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    average_cost: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    weight_percentage: Decimal = Field(default=Decimal("0"), ge=Decimal("0"), le=Decimal("100"))


class HoldingRecord(HoldingBase):
    id: int
    created_at: datetime
    updated_at: datetime


class InvestmentThesisBase(BaseModel):
    asset_id: int
    strategy_tag: str | None = Field(default=None, max_length=50)
    expected_dividend_yield: Decimal | None = Field(default=None, ge=Decimal("0"))
    margin_of_safety: Decimal | None = Field(default=None, ge=Decimal("0"))
    valuation_metric_name: str | None = Field(default=None, max_length=50)
    percentile_value: int | None = Field(default=None, ge=0, le=100)
    short_description: str | None = Field(default=None, max_length=500)
    markdown_details: str | None = None


class InvestmentThesisRecord(InvestmentThesisBase):
    id: int
    created_at: datetime
    updated_at: datetime


class PerformanceHistoryBase(BaseModel):
    portfolio_id: int
    record_date: date
    portfolio_nav: Decimal = Field(ge=Decimal("0"))
    benchmark_nav: Decimal | None = Field(default=None, ge=Decimal("0"))


class PerformanceHistoryRecord(PerformanceHistoryBase):
    id: int
    created_at: datetime
    updated_at: datetime


class PortfolioHoldingView(BaseModel):
    holding: HoldingRecord
    asset: AssetRecord
    investment_thesis: InvestmentThesisRecord | None = None


class PortfolioAggregateView(BaseModel):
    portfolio: PortfolioRecord
    holdings: list[PortfolioHoldingView] = Field(default_factory=list)
    performance_history: list[PerformanceHistoryRecord] = Field(default_factory=list)
