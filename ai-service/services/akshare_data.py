from functools import lru_cache

import akshare as ak
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

    def get_share_count_series(self, symbol: str) -> pd.Series:
        normalized_symbol = normalize_stock_symbol(symbol)
        return self._get_share_count_series_cached(normalized_symbol).copy()

    @lru_cache(maxsize=128)
    def _get_share_count_series_cached(self, symbol: str) -> pd.Series:
        stock_change_symbol = self._to_gbjg_symbol(symbol)
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
