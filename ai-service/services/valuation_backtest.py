import os
from functools import lru_cache
from pathlib import Path

import akshare as ak
import numpy as np
import pandas as pd
from config import settings


MIN_RISK_FREE_RATE = 0.02
PROXY_DOMAINS = [
    "fund.eastmoney.com",
    "push2.eastmoney.com",
    "push2his.eastmoney.com",
    "emweb.securities.eastmoney.com",
]


def _normalize_symbol(symbol: str) -> str:
    normalized = (symbol or "").strip().lower()
    if normalized.startswith(("sh", "sz", "bj")):
        normalized = normalized[2:]
    if not normalized.isdigit():
        raise ValueError("股票代码格式无效，请输入 6 位 A 股代码，例如 600519")
    return normalized


def _safe_float(value) -> float | None:
    if value is None:
        return None
    if isinstance(value, str):
        cleaned = value.replace(",", "").replace("%", "").strip()
        if not cleaned:
            return None
        value = cleaned
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if pd.isna(result):
        return None
    return result


def _normalize_rate_input(value) -> float | None:
    rate = _safe_float(value)
    if rate is None:
        return None
    if rate >= 1:
        rate /= 100
    return rate


class ValuationBacktestService:
    def __init__(self, bond_yield_path: str | Path | None = None):
        self.bond_yield_path = Path(
            bond_yield_path or Path(__file__).resolve().parents[1] / "assets" / "中国十年期国债收益率历史数据.csv"
        )

    def get_backtest(
        self,
        symbol: str,
        start_date: str | None = None,
        end_date: str | None = None,
        valuation_mode: str | None = None,
        equity_bond_spread: float | str | None = None,
        manual_reasonable_pe: float | str | None = None,
    ) -> list[dict]:
        stock_symbol = _normalize_symbol(symbol)
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

        manual_pe = _safe_float(manual_reasonable_pe) if mode == "manual_pe" else None
        if mode == "manual_pe" and (manual_pe is None or manual_pe <= 0):
            raise ValueError("手动输入的合理市盈率必须大于 0")

        price_df = self._fetch_price_history(stock_symbol, start, end)
        if price_df.empty:
            return []

        share_count_series = self._fetch_share_count_series(stock_symbol)
        profit_df = self._build_profit_series(stock_symbol)
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

    def _fetch_price_history(self, symbol: str, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
        return self._fetch_price_history_cached(symbol, start.strftime("%Y%m%d"), end.strftime("%Y%m%d")).copy()

    @lru_cache(maxsize=128)
    def _fetch_price_history_cached(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        self._install_proxy_patch_if_available()
        price_df = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust="",
        )
        if price_df.empty:
            return pd.DataFrame(columns=["date", "close"])

        normalized = price_df.rename(columns={"日期": "date", "收盘": "close"})[["date", "close"]].copy()
        normalized["date"] = pd.to_datetime(normalized["date"])
        normalized["close"] = pd.to_numeric(normalized["close"], errors="coerce")
        return normalized.dropna().sort_values("date").reset_index(drop=True)

    def _fetch_share_count_series(self, symbol: str) -> pd.Series:
        return self._fetch_share_count_series_cached(symbol).copy()

    @lru_cache(maxsize=128)
    def _fetch_share_count_series_cached(self, symbol: str) -> pd.Series:
        stock_change_symbol = self._to_gbjg_symbol(symbol)
        history_df = ak.stock_zh_a_gbjg_em(symbol=stock_change_symbol)
        if history_df.empty:
            latest_share_count = self._fetch_latest_share_count(symbol)
            return pd.Series(
                [latest_share_count],
                index=pd.DatetimeIndex([pd.Timestamp("1990-01-01")]),
                name="share_count",
                dtype=float,
            )

        history_df = history_df.rename(
            columns={
                "变更日期": "date",
                "总股本": "total_share_count",
                "已上市流通A股": "listed_a_share_count",
                "已流通股份": "circulating_share_count",
            }
        ).copy()
        history_df["date"] = pd.to_datetime(history_df["date"], errors="coerce")

        share_column = None
        for column_name in ("total_share_count", "listed_a_share_count", "circulating_share_count"):
            if column_name in history_df.columns:
                history_df[column_name] = pd.to_numeric(history_df[column_name], errors="coerce")
                if history_df[column_name].notna().any():
                    share_column = column_name
                    break

        if share_column is None:
            latest_share_count = self._fetch_latest_share_count(symbol)
            return pd.Series(
                [latest_share_count],
                index=pd.DatetimeIndex([pd.Timestamp("1990-01-01")]),
                name="share_count",
                dtype=float,
            )

        history_df["share_count"] = history_df[share_column]
        history_df = history_df.dropna(subset=["date", "share_count"]).sort_values("date")
        history_df = history_df.drop_duplicates(subset=["date"], keep="last")
        if history_df.empty:
            latest_share_count = self._fetch_latest_share_count(symbol)
            return pd.Series(
                [latest_share_count],
                index=pd.DatetimeIndex([pd.Timestamp("1990-01-01")]),
                name="share_count",
                dtype=float,
            )

        return pd.Series(
            history_df["share_count"].to_numpy(dtype=float),
            index=pd.DatetimeIndex(history_df["date"]),
            name="share_count",
        )

    def _fetch_latest_share_count(self, symbol: str) -> float:
        return float(self._fetch_latest_share_count_cached(symbol))

    @lru_cache(maxsize=128)
    def _fetch_latest_share_count_cached(self, symbol: str) -> float:
        info_df = ak.stock_individual_info_em(symbol=symbol)
        if info_df.empty:
            raise ValueError("未获取到股票股本信息")

        for item_name in ("总股本", "流通股"):
            match = info_df.loc[info_df["item"] == item_name, "value"]
            if not match.empty:
                share_count = _safe_float(match.iloc[0])
                if share_count and share_count > 0:
                    return share_count
        raise ValueError("股本信息缺失，无法换算每股估值")

    def _to_gbjg_symbol(self, symbol: str) -> str:
        if symbol.startswith(("6", "5", "9")):
            market = "SH"
        elif symbol.startswith(("4", "8")):
            market = "BJ"
        else:
            market = "SZ"
        return f"{symbol}.{market}"

    def _build_profit_series(self, symbol: str) -> pd.DataFrame:
        return self._build_profit_series_cached(symbol).copy()

    @lru_cache(maxsize=128)
    def _build_profit_series_cached(self, symbol: str) -> pd.DataFrame:
        financial_df = ak.stock_financial_abstract(symbol=symbol)
        if financial_df.empty:
            return pd.DataFrame(columns=["date", "ttm_profit"])

        profit_row = financial_df.loc[financial_df["指标"] == "归母净利润"]
        if profit_row.empty:
            raise ValueError("财报摘要中未找到“归母净利润”字段")

        series_items = []
        row = profit_row.iloc[0]
        for column_name, value in row.items():
            if column_name in {"选项", "指标"}:
                continue
            report_date = pd.to_datetime(column_name, format="%Y%m%d", errors="coerce")
            profit_value = _safe_float(value)
            if pd.isna(report_date) or profit_value is None:
                continue
            series_items.append({"date": report_date.normalize(), "cumulative_profit": profit_value})

        if not series_items:
            return pd.DataFrame(columns=["date", "ttm_profit"])

        cumulative_df = pd.DataFrame(series_items).sort_values("date").reset_index(drop=True)
        cumulative_map = {row.date: row.cumulative_profit for row in cumulative_df.itertuples(index=False)}

        results = []
        for row in cumulative_df.itertuples(index=False):
            month = row.date.month
            quarter = (month - 1) // 3 + 1
            year = row.date.year

            if quarter == 1:
                quarter_profit = row.cumulative_profit
            else:
                previous_quarter_date = pd.Timestamp(year=year, month=(quarter - 1) * 3, day=1) + pd.offsets.MonthEnd(0)
                previous_cumulative = cumulative_map.get(previous_quarter_date)
                quarter_profit = row.cumulative_profit - previous_cumulative if previous_cumulative is not None else None

            annual_date = pd.Timestamp(year=year - 1, month=12, day=31)
            same_quarter_last_year = pd.Timestamp(year=year - 1, month=month, day=1) + pd.offsets.MonthEnd(0)
            previous_annual = cumulative_map.get(annual_date)
            previous_same_quarter = cumulative_map.get(same_quarter_last_year)

            if quarter == 4:
                ttm_profit = row.cumulative_profit
            elif previous_annual is not None and previous_same_quarter is not None:
                ttm_profit = previous_annual + row.cumulative_profit - previous_same_quarter
            elif quarter_profit is not None:
                ttm_profit = quarter_profit * 4
            else:
                ttm_profit = None

            if ttm_profit is not None:
                results.append({"date": row.date, "ttm_profit": float(ttm_profit)})

        return pd.DataFrame(results).sort_values("date").reset_index(drop=True)

    def _install_proxy_patch_if_available(self) -> None:
        if getattr(self, "_proxy_initialized", False):
            return

        try:
            import akshare_proxy_patch
        except ImportError as exc:
            raise RuntimeError("缺少 akshare_proxy_patch，无法通过代理抓取历史行情") from exc

        if not settings.AKSHARE_PROXY_TOKEN:
            raise RuntimeError("缺少 AKSHARE_PROXY_TOKEN 环境变量，无法通过代理抓取历史行情")

        akshare_proxy_patch.install_patch(
            settings.AKSHARE_PROXY_HOST,
            auth_token=settings.AKSHARE_PROXY_TOKEN,
            retry=settings.AKSHARE_PROXY_RETRY,
            hook_domains=PROXY_DOMAINS,
        )
        self._proxy_initialized = True

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
