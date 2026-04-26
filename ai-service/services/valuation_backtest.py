from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

from services.akshare_data import AkshareDataService, normalize_stock_symbol, safe_float


MIN_RISK_FREE_RATE = 0.02


def _normalize_rate_input(value) -> float | None:
    rate = safe_float(value)
    if rate is None:
        return None
    if rate >= 1:
        rate /= 100
    return rate


class ValuationBacktestService:
    def __init__(
        self,
        bond_yield_path: str | Path | None = None,
        akshare_service: AkshareDataService | None = None,
    ):
        self.bond_yield_path = Path(
            bond_yield_path or Path(__file__).resolve().parents[1] / "assets" / "中国十年期国债收益率历史数据.csv"
        )
        self.akshare_service = akshare_service or AkshareDataService()

    def get_backtest(
        self,
        symbol: str,
        start_date: str | None = None,
        end_date: str | None = None,
        valuation_mode: str | None = None,
        equity_bond_spread: float | str | None = None,
        manual_reasonable_pe: float | str | None = None,
    ) -> list[dict]:
        stock_symbol = normalize_stock_symbol(symbol)
        start = pd.Timestamp(start_date or "2010-01-01").normalize()
        end = pd.Timestamp(end_date or pd.Timestamp.today().strftime("%Y-%m-%d")).normalize()
        if start >= end:
            raise ValueError("开始日期必须早于结束日期")

        mode = (valuation_mode or "spread").strip().lower()
        if mode not in {"spread", "manual_pe", "peg1"}:
            raise ValueError("估值模式无效，仅支持 spread、manual_pe 或 peg1")

        spread_rate = _normalize_rate_input(equity_bond_spread) if mode == "spread" else None
        if mode == "spread" and spread_rate is None:
            spread_rate = 0.0
        if spread_rate is not None and spread_rate < 0:
            raise ValueError("股债利差不能为负数")

        manual_pe = safe_float(manual_reasonable_pe) if mode == "manual_pe" else None
        if mode == "manual_pe" and (manual_pe is None or manual_pe <= 0):
            raise ValueError("手动输入的合理市盈率必须大于 0")

        price_df = self.akshare_service.get_price_history(stock_symbol, start, end)
        if price_df.empty:
            return []

        share_count_series = self.akshare_service.get_share_count_series(stock_symbol)
        profit_df = self.akshare_service.get_ttm_profit_series(stock_symbol)
        if profit_df.empty:
            raise ValueError("未获取到归母净利润数据")

        smoothed_profit = self._sample_series_at_dates(
            profit_df.set_index("date")["ttm_profit"],
            pd.DatetimeIndex(price_df["date"]),
            allow_extrapolation=False,
        )
        past_dates = pd.DatetimeIndex(price_df["date"] - pd.DateOffset(years=5))
        profit_5y_ago = self._sample_series_at_dates(
            profit_df.set_index("date")["ttm_profit"],
            past_dates,
            allow_extrapolation=False,
        )
        share_count = self._sample_series_at_dates(
            share_count_series,
            pd.DatetimeIndex(price_df["date"]),
            allow_extrapolation=True,
        )

        if mode == "spread":
            bond_yield = self._sample_series_at_dates(
                self._load_bond_yield_series(),
                pd.DatetimeIndex(price_df["date"]),
                allow_extrapolation=True,
            ).clip(lower=MIN_RISK_FREE_RATE)
            risk_free = bond_yield
        else:
            risk_free = pd.Series(np.nan, index=pd.DatetimeIndex(price_df["date"]), dtype=float)

        merged = price_df.copy()
        merged["smoothed_profit"] = smoothed_profit.to_numpy()
        merged["profit_5y_ago"] = profit_5y_ago.to_numpy()
        merged["risk_free_rate"] = risk_free.to_numpy()
        merged["share_count"] = share_count.to_numpy()

        valid_growth = (
            merged["smoothed_profit"].notna()
            & merged["profit_5y_ago"].notna()
            & (merged["smoothed_profit"] > 0)
            & (merged["profit_5y_ago"] > 0)
            & merged["share_count"].notna()
            & (merged["share_count"] > 0)
        )
        merged = merged.loc[valid_growth].copy()
        if merged.empty:
            return []

        merged["growth_rate"] = (merged["smoothed_profit"] / merged["profit_5y_ago"]) ** (1 / 5) - 1
        merged["projected_profit"] = merged["smoothed_profit"] * (1 + merged["growth_rate"]) ** 3

        if mode == "manual_pe":
            merged["reasonable_pe"] = float(manual_pe)
        elif mode == "peg1":
            merged["reasonable_pe"] = merged["growth_rate"] * 100
        else:
            merged["reasonable_pe"] = 1 / (merged["risk_free_rate"] + float(spread_rate))

        merged = merged.loc[merged["reasonable_pe"].notna() & (merged["reasonable_pe"] > 0)].copy()
        if merged.empty:
            return []

        merged["intrinsic_value"] = merged["smoothed_profit"] * merged["reasonable_pe"] / merged["share_count"]
        merged["buy_line"] = merged["projected_profit"] * merged["reasonable_pe"] * 0.5 / merged["share_count"]
        projected_sell = merged["projected_profit"] * merged["reasonable_pe"] * 1.5 / merged["share_count"]
        pe50_sell = merged["smoothed_profit"] * 50 / merged["share_count"]
        merged["sell_line"] = projected_sell.where(projected_sell < pe50_sell, pe50_sell)
        merged = merged.dropna(subset=["close", "intrinsic_value", "buy_line", "sell_line"])

        records = []
        for row in merged.itertuples(index=False):
            records.append(
                {
                    "date": row.date.strftime("%Y-%m-%d"),
                    "price": round(float(row.close), 4),
                    "intrinsic_value": round(float(row.intrinsic_value), 4),
                    "buy_line": round(float(row.buy_line), 4),
                    "sell_line": round(float(row.sell_line), 4),
                }
            )
        return records

    @lru_cache(maxsize=1)
    def _load_bond_yield_series(self) -> pd.Series:
        df = pd.read_csv(self.bond_yield_path, encoding="utf-8-sig")
        df = df.rename(columns={"日期": "date", "收盘": "close"})[["date", "close"]].copy()
        df["date"] = pd.to_datetime(df["date"])
        df["close"] = pd.to_numeric(df["close"], errors="coerce") / 100
        df = df.dropna().sort_values("date")
        return pd.Series(df["close"].to_numpy(), index=pd.DatetimeIndex(df["date"]), name="risk_free_rate")

    def _sample_series_at_dates(self, series: pd.Series, target_dates: pd.DatetimeIndex, allow_extrapolation: bool) -> pd.Series:
        if series.empty or len(target_dates) == 0:
            return pd.Series(dtype=float)

        base = series.sort_index()
        base = base[~base.index.duplicated(keep="last")]
        base = base.dropna()
        if base.empty:
            return pd.Series(index=pd.DatetimeIndex(target_dates), dtype=float)

        base_index = pd.to_datetime(base.index).astype("datetime64[ns]")
        base_x = base_index.asi8.astype(np.float64)
        base_y = base.to_numpy(dtype=np.float64)
        target_index = pd.to_datetime(pd.DatetimeIndex(target_dates)).astype("datetime64[ns]")
        target_x = target_index.asi8.astype(np.float64)

        sampled_values = np.interp(target_x, base_x, base_y)

        if not allow_extrapolation:
            outside_mask = (target_x < base_x[0]) | (target_x > base_x[-1])
            sampled_values[outside_mask] = np.nan

        return pd.Series(sampled_values, index=target_index, dtype=float)
