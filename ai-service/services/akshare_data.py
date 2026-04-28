from datetime import date, timedelta
from functools import lru_cache
from contextlib import contextmanager
import os

import akshare as ak
import akshare_proxy_patch
import pandas as pd

from config import settings


PROXY_DOMAINS = [
    "fund.eastmoney.com",
    "push2.eastmoney.com",
    "push2his.eastmoney.com",
    "emweb.securities.eastmoney.com",
]


def normalize_stock_symbol(symbol: str) -> str:
    normalized = (symbol or "").strip().lower()
    if normalized.startswith(("sh", "sz", "bj")):
        normalized = normalized[2:]
    if not normalized.isdigit():
        raise ValueError("股票代码格式无效，请输入 6 位 A 股代码，例如 600519")
    return normalized


def safe_float(value) -> float | None:
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


class AkshareDataService:
    def get_latest_asset_price(self, ticker_code: str, asset_type: str) -> tuple[date, float]:
        normalized_type = (asset_type or "").strip().lower()
        if normalized_type == "etf":
            return self.get_latest_etf_price(ticker_code)
        if normalized_type == "fund":
            return self.get_latest_passive_fund_nav(ticker_code)
        return self.get_latest_stock_price(ticker_code)

    def get_latest_stock_price(self, ticker_code: str) -> tuple[date, float]:
        normalized_symbol = self._extract_numeric_symbol(ticker_code)
        end = pd.Timestamp.today().normalize()
        start = end - pd.Timedelta(days=14)
        price_df = self._get_price_history_cached(
            normalized_symbol,
            start.strftime("%Y%m%d"),
            end.strftime("%Y%m%d"),
        ).copy()
        if price_df.empty:
            raise ValueError(f"未获取到股票 {ticker_code} 的最新价格")
        latest = price_df.iloc[-1]
        return latest["date"].date(), float(latest["close"])

    def get_latest_etf_price(self, ticker_code: str) -> tuple[date, float]:
        symbol = self._to_exchange_prefixed_symbol(ticker_code)
        self._try_install_proxy_patch_if_available()
        with self._without_system_proxies():
            history_df = ak.fund_etf_hist_sina(symbol=symbol)
        normalized = self._normalize_price_dataframe(history_df)
        if normalized.empty:
            raise ValueError(f"未获取到 ETF {ticker_code} 的最新价格")
        latest = normalized.iloc[-1]
        return latest["date"].date(), float(latest["close"])

    def get_latest_passive_fund_nav(self, ticker_code: str) -> tuple[date, float]:
        fund_code = self._extract_numeric_symbol(ticker_code)
        self._try_install_proxy_patch_if_available()
        with self._without_system_proxies():
            nav_df = ak.fund_open_fund_info_em(symbol=fund_code, indicator="单位净值走势")
        normalized = self._normalize_price_dataframe(nav_df)
        if normalized.empty:
            raise ValueError(f"未获取到基金 {ticker_code} 的最新净值")
        latest = normalized.iloc[-1]
        return latest["date"].date(), float(latest["close"])

    def get_passive_index_fund_metadata(self, fund_code: str) -> dict[str, str] | None:
        normalized_fund_code = self._extract_numeric_symbol(fund_code)
        self._try_install_proxy_patch_if_available()
        with self._without_system_proxies():
            fund_df = ak.fund_info_index_em(symbol="沪深指数", indicator="被动指数型")
        if fund_df.empty or "基金代码" not in fund_df.columns:
            return None
        match = fund_df.loc[fund_df["基金代码"].astype(str) == normalized_fund_code]
        if match.empty:
            return None
        return {str(key): str(value) for key, value in match.iloc[0].to_dict().items()}

    def get_index_history(self, symbol: str = "sh000300", start_date: date | None = None, end_date: date | None = None) -> pd.DataFrame:
        return self._get_index_history_cached(
            symbol.lower(),
            start_date.isoformat() if start_date else "",
            end_date.isoformat() if end_date else "",
        ).copy()

    def get_index_close_on_or_before(self, symbol: str, target_date: date) -> tuple[date, float]:
        start_date = target_date - timedelta(days=20)
        history_df = self.get_index_history(symbol=symbol, start_date=start_date, end_date=target_date)
        eligible = history_df.loc[history_df["date"].dt.date <= target_date]
        if eligible.empty:
            raise ValueError(f"未获取到指数 {symbol} 在 {target_date} 及以前的收盘价")
        latest = eligible.iloc[-1]
        return latest["date"].date(), float(latest["close"])

    def get_price_history(self, symbol: str, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
        normalized_symbol = normalize_stock_symbol(symbol)
        return self._get_price_history_cached(
            normalized_symbol,
            start.strftime("%Y%m%d"),
            end.strftime("%Y%m%d"),
        ).copy()

    @lru_cache(maxsize=128)
    def _get_price_history_cached(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        self._install_proxy_patch_if_available()
        with self._without_system_proxies():
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

    @lru_cache(maxsize=32)
    def _get_index_history_cached(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        self._try_install_proxy_patch_if_available()
        with self._without_system_proxies():
            history_df = ak.stock_zh_index_daily(symbol=symbol)
        if history_df.empty:
            return pd.DataFrame(columns=["date", "close"])

        if "date" in history_df.columns:
            normalized = history_df.copy()
        else:
            normalized = history_df.reset_index()
            normalized = normalized.rename(columns={normalized.columns[0]: "date"})

        close_column = "close" if "close" in normalized.columns else "收盘"
        normalized = normalized.rename(columns={close_column: "close"})[["date", "close"]].copy()
        normalized["date"] = pd.to_datetime(normalized["date"], errors="coerce")
        normalized["close"] = pd.to_numeric(normalized["close"], errors="coerce")
        normalized = normalized.dropna().sort_values("date").reset_index(drop=True)

        if start_date:
            normalized = normalized.loc[normalized["date"] >= pd.Timestamp(start_date)]
        if end_date:
            normalized = normalized.loc[normalized["date"] <= pd.Timestamp(end_date)]
        return normalized.reset_index(drop=True)

    def get_share_count_series(self, symbol: str) -> pd.Series:
        normalized_symbol = normalize_stock_symbol(symbol)
        return self._get_share_count_series_cached(normalized_symbol).copy()

    @lru_cache(maxsize=128)
    def _get_share_count_series_cached(self, symbol: str) -> pd.Series:
        stock_change_symbol = self._to_gbjg_symbol(symbol)
        with self._without_system_proxies():
            history_df = ak.stock_zh_a_gbjg_em(symbol=stock_change_symbol)
        if history_df.empty:
            latest_share_count = self.get_latest_share_count(symbol)
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
            latest_share_count = self.get_latest_share_count(symbol)
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
            latest_share_count = self.get_latest_share_count(symbol)
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

    def get_latest_share_count(self, symbol: str) -> float:
        normalized_symbol = normalize_stock_symbol(symbol)
        return float(self._get_latest_share_count_cached(normalized_symbol))

    @lru_cache(maxsize=128)
    def _get_latest_share_count_cached(self, symbol: str) -> float:
        with self._without_system_proxies():
            info_df = ak.stock_individual_info_em(symbol=symbol)
        if info_df.empty:
            raise ValueError("未获取到股票股本信息")

        for item_name in ("总股本", "流通股"):
            match = info_df.loc[info_df["item"] == item_name, "value"]
            if not match.empty:
                share_count = safe_float(match.iloc[0])
                if share_count and share_count > 0:
                    return share_count
        raise ValueError("股本信息缺失，无法换算每股估值")

    def get_ttm_profit_series(self, symbol: str) -> pd.DataFrame:
        normalized_symbol = normalize_stock_symbol(symbol)
        return self._get_ttm_profit_series_cached(normalized_symbol).copy()

    @lru_cache(maxsize=128)
    def _get_ttm_profit_series_cached(self, symbol: str) -> pd.DataFrame:
        with self._without_system_proxies():
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
            profit_value = safe_float(value)
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

    def _to_gbjg_symbol(self, symbol: str) -> str:
        if symbol.startswith(("6", "5", "9")):
            market = "SH"
        elif symbol.startswith(("4", "8")):
            market = "BJ"
        else:
            market = "SZ"
        return f"{symbol}.{market}"

    def _extract_numeric_symbol(self, ticker_code: str) -> str:
        normalized = (ticker_code or "").strip().lower()
        for separator in (".",):
            if separator in normalized:
                left, right = normalized.split(separator, 1)
                if left.isdigit():
                    return left
                if right.isdigit():
                    return right
        if normalized.startswith(("sh", "sz", "bj")) and normalized[2:].isdigit():
            return normalized[2:]
        if normalized.isdigit():
            return normalized
        raise ValueError(f"无法识别证券代码: {ticker_code}")

    def _to_exchange_prefixed_symbol(self, ticker_code: str) -> str:
        normalized = (ticker_code or "").strip().lower()
        if normalized.startswith(("sh", "sz", "bj")) and normalized[2:].isdigit():
            return normalized
        if "." in normalized:
            left, right = normalized.split(".", 1)
            if left.isdigit():
                return f"{right.lower()}{left}"
        numeric_symbol = self._extract_numeric_symbol(ticker_code)
        if numeric_symbol.startswith(("6", "5", "9")):
            prefix = "sh"
        elif numeric_symbol.startswith(("4", "8")):
            prefix = "bj"
        else:
            prefix = "sz"
        return f"{prefix}{numeric_symbol}"

    def _normalize_price_dataframe(self, history_df: pd.DataFrame) -> pd.DataFrame:
        if history_df.empty:
            return pd.DataFrame(columns=["date", "close"])

        normalized = history_df.copy()
        rename_candidates = {
            "date": "date",
            "日期": "date",
            "净值日期": "date",
            "close": "close",
            "收盘": "close",
            "单位净值": "close",
            "最新价": "close",
        }
        normalized = normalized.rename(
            columns={column: rename_candidates[column] for column in normalized.columns if column in rename_candidates}
        )

        if "date" not in normalized.columns:
            normalized = normalized.reset_index()
            normalized = normalized.rename(columns={normalized.columns[0]: "date"})
        if "close" not in normalized.columns:
            raise ValueError(f"未识别的价格字段: {list(history_df.columns)}")

        normalized = normalized[["date", "close"]].copy()
        normalized["date"] = pd.to_datetime(normalized["date"], errors="coerce")
        normalized["close"] = pd.to_numeric(normalized["close"], errors="coerce")
        return normalized.dropna().sort_values("date").reset_index(drop=True)

    def _install_proxy_patch_if_available(self) -> None:
        if getattr(self, "_proxy_initialized", False):
            return

        akshare_proxy_patch.install_patch(
            settings.AKSHARE_PROXY_HOST,
            auth_token=settings.AKSHARE_PROXY_TOKEN,
            retry=settings.AKSHARE_PROXY_RETRY,
            hook_domains=PROXY_DOMAINS,
        )
        self._proxy_initialized = True

    def _try_install_proxy_patch_if_available(self) -> None:
        if getattr(self, "_proxy_initialized", False):
            return
        if not settings.AKSHARE_PROXY_TOKEN:
            return
        try:
            self._install_proxy_patch_if_available()
        except Exception:
            return

    @contextmanager
    def _without_system_proxies(self):
        proxy_keys = [
            "HTTP_PROXY",
            "HTTPS_PROXY",
            "ALL_PROXY",
            "http_proxy",
            "https_proxy",
            "all_proxy",
        ]
        original_values = {key: os.environ.get(key) for key in proxy_keys}
        try:
            for key in proxy_keys:
                os.environ.pop(key, None)
            yield
        finally:
            for key, value in original_values.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
