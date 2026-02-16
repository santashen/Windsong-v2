import logging
from datetime import datetime, timedelta

import akshare as ak
import pandas as pd

logger = logging.getLogger(__name__)


class FinanceDataService:
    """Service for fetching stock and fund data via akshare."""

    def __init__(self):
        self._stock_list = None
        self._fund_list = None

    def _get_stock_list(self) -> pd.DataFrame:
        """Get and cache the A-share stock list."""
        if self._stock_list is None:
            try:
                self._stock_list = ak.stock_info_a_code_name()
            except Exception as e:
                logger.error(f"Failed to fetch stock list: {e}")
                return pd.DataFrame(columns=["code", "name"])
        return self._stock_list

    def _get_fund_list(self) -> pd.DataFrame:
        """Get and cache the open-end fund list."""
        if self._fund_list is None:
            try:
                df = ak.fund_name_em()
                self._fund_list = df[["基金代码", "基金简称"]].rename(
                    columns={"基金代码": "code", "基金简称": "name"}
                )
            except Exception as e:
                logger.error(f"Failed to fetch fund list: {e}")
                return pd.DataFrame(columns=["code", "name"])
        return self._fund_list

    def search(self, keyword: str, limit: int = 20) -> list[dict]:
        """Search stocks and funds by keyword (name or code)."""
        if not keyword or len(keyword.strip()) == 0:
            return []

        keyword = keyword.strip()
        results = []

        # Search stocks
        try:
            stock_df = self._get_stock_list()
            if not stock_df.empty:
                mask = stock_df["code"].str.contains(keyword, case=False, na=False) | \
                       stock_df["name"].str.contains(keyword, case=False, na=False)
                matched = stock_df[mask].head(limit)
                for _, row in matched.iterrows():
                    results.append({
                        "code": row["code"],
                        "name": row["name"],
                        "type": "stock",
                    })
        except Exception as e:
            logger.warning(f"Stock search error: {e}")

        # Search funds
        try:
            fund_df = self._get_fund_list()
            if not fund_df.empty:
                mask = fund_df["code"].str.contains(keyword, case=False, na=False) | \
                       fund_df["name"].str.contains(keyword, case=False, na=False)
                matched = fund_df[mask].head(limit)
                for _, row in matched.iterrows():
                    results.append({
                        "code": row["code"],
                        "name": row["name"],
                        "type": "fund",
                    })
        except Exception as e:
            logger.warning(f"Fund search error: {e}")

        return results[:limit]

    def get_stock_history(
        self, code: str, start: str, end: str
    ) -> dict:
        """Fetch stock historical data."""
        try:
            df = ak.stock_zh_a_hist(
                symbol=code,
                period="daily",
                start_date=start.replace("-", ""),
                end_date=end.replace("-", ""),
                adjust="qfq",
            )
            if df.empty:
                return {"code": code, "type": "stock", "dates": [], "data": {}}

            result = {
                "code": code,
                "type": "stock",
                "dates": df["日期"].astype(str).tolist(),
                "data": {
                    "close": df["收盘"].tolist(),
                    "open": df["开盘"].tolist(),
                    "high": df["最高"].tolist(),
                    "low": df["最低"].tolist(),
                    "volume": df["成交量"].tolist(),
                    "turnover_rate": df["换手率"].tolist() if "换手率" in df.columns else [],
                },
            }
            return result
        except Exception as e:
            logger.error(f"Failed to fetch stock history for {code}: {e}")
            raise

    def get_fund_history(
        self, code: str, start: str, end: str
    ) -> dict:
        """Fetch fund NAV history data."""
        try:
            df = ak.fund_open_fund_info_em(symbol=code, indicator="单位净值走势")
            if df.empty:
                return {"code": code, "type": "fund", "dates": [], "data": {}}

            # Filter by date range
            df["净值日期"] = pd.to_datetime(df["净值日期"])
            mask = (df["净值日期"] >= start) & (df["净值日期"] <= end)
            df = df[mask].sort_values("净值日期")

            dates = df["净值日期"].dt.strftime("%Y-%m-%d").tolist()
            nav = df["单位净值"].tolist()

            # Try to get cumulative NAV
            cum_nav = []
            daily_return = []
            try:
                df_cum = ak.fund_open_fund_info_em(symbol=code, indicator="累计净值走势")
                df_cum["净值日期"] = pd.to_datetime(df_cum["净值日期"])
                df_cum = df_cum[(df_cum["净值日期"] >= start) & (df_cum["净值日期"] <= end)]
                df_cum = df_cum.sort_values("净值日期")
                cum_nav = df_cum["累计净值"].tolist()
            except Exception:
                pass

            # Calculate daily return from NAV
            if nav:
                daily_return = [0.0] + [
                    round((nav[i] - nav[i - 1]) / nav[i - 1] * 100, 4)
                    if nav[i - 1] != 0 else 0.0
                    for i in range(1, len(nav))
                ]

            result = {
                "code": code,
                "type": "fund",
                "dates": dates,
                "data": {
                    "nav": nav,
                    "cum_nav": cum_nav,
                    "daily_return": daily_return,
                },
            }
            return result
        except Exception as e:
            logger.error(f"Failed to fetch fund history for {code}: {e}")
            raise

    def get_history(
        self, code: str, data_type: str, start: str, end: str
    ) -> dict:
        """Fetch historical data based on type."""
        if data_type == "fund":
            return self.get_fund_history(code, start, end)
        else:
            return self.get_stock_history(code, start, end)
