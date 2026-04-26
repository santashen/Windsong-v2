from __future__ import annotations

from models import AssetBase, HoldingBase, InvestmentThesisBase, PerformanceHistoryBase, PortfolioBase
from repositories import FamilyPortfolioRepository


class FamilyPortfolioService:
    def __init__(self, repository: FamilyPortfolioRepository | None = None):
        self.repository = repository or FamilyPortfolioRepository()

    def list_portfolios(self) -> dict:
        portfolios = self.repository.list_portfolios()
        return {"items": [portfolio.model_dump(mode="json") for portfolio in portfolios]}

    def create_portfolio(self, payload: PortfolioBase) -> dict:
        portfolio = self.repository.create_portfolio(payload)
        return portfolio.model_dump(mode="json")

    def update_portfolio(self, portfolio_id: int, payload: PortfolioBase) -> dict | None:
        portfolio = self.repository.update_portfolio(portfolio_id, payload)
        return portfolio.model_dump(mode="json") if portfolio else None

    def delete_portfolio(self, portfolio_id: int) -> bool:
        return self.repository.delete_portfolio(portfolio_id)

    def list_assets(self) -> dict:
        assets = self.repository.list_assets()
        return {"items": [asset.model_dump(mode="json") for asset in assets]}

    def create_asset(self, payload: AssetBase) -> dict:
        asset = self.repository.create_asset(payload)
        return asset.model_dump(mode="json")

    def update_asset(self, asset_id: int, payload: AssetBase) -> dict | None:
        asset = self.repository.update_asset(asset_id, payload)
        return asset.model_dump(mode="json") if asset else None

    def delete_asset(self, asset_id: int) -> bool:
        return self.repository.delete_asset(asset_id)

    def create_holding(self, payload: HoldingBase) -> dict:
        holding = self.repository.create_holding(payload)
        return holding.model_dump(mode="json")

    def update_holding(self, holding_id: int, payload: HoldingBase) -> dict | None:
        holding = self.repository.update_holding(holding_id, payload)
        return holding.model_dump(mode="json") if holding else None

    def delete_holding(self, holding_id: int) -> bool:
        return self.repository.delete_holding(holding_id)

    def create_investment_thesis(self, payload: InvestmentThesisBase) -> dict:
        thesis = self.repository.create_investment_thesis(payload)
        return thesis.model_dump(mode="json")

    def update_investment_thesis(self, thesis_id: int, payload: InvestmentThesisBase) -> dict | None:
        thesis = self.repository.update_investment_thesis(thesis_id, payload)
        return thesis.model_dump(mode="json") if thesis else None

    def delete_investment_thesis(self, thesis_id: int) -> bool:
        return self.repository.delete_investment_thesis(thesis_id)

    def create_performance_history(self, payload: PerformanceHistoryBase) -> dict:
        history = self.repository.create_performance_history(payload)
        return history.model_dump(mode="json")

    def update_performance_history(
        self, history_id: int, payload: PerformanceHistoryBase
    ) -> dict | None:
        history = self.repository.update_performance_history(history_id, payload)
        return history.model_dump(mode="json") if history else None

    def delete_performance_history(self, history_id: int) -> bool:
        return self.repository.delete_performance_history(history_id)

    def get_portfolio_detail(self, portfolio_id: int) -> dict | None:
        aggregate = self.repository.get_portfolio_aggregate(portfolio_id)
        if aggregate is None:
            return None
        return aggregate.model_dump(mode="json")
