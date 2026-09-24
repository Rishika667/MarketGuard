from __future__ import annotations

import time
from datetime import date

import pandas as pd
import yfinance as yf

from marketguard.adapters.base import BaseMarketDataAdapter, SourcePayload


class YahooFinanceAdapter(BaseMarketDataAdapter):
    """Yahoo Finance adapter for EOD OHLCV and corporate actions."""

    source_name = "yahoo_finance"

    def __init__(self, request_sleep_seconds: float = 0.0) -> None:
        self.request_sleep_seconds = request_sleep_seconds

    def fetch_security_data(self, symbol: str, start_date: date, end_date: date) -> SourcePayload:
        if self.request_sleep_seconds > 0:
            time.sleep(self.request_sleep_seconds)

        market_df = yf.download(
            tickers=symbol,
            start=start_date.isoformat(),
            end=end_date.isoformat(),
            auto_adjust=False,
            progress=False,
            actions=False,
            group_by="column",
            threads=False,
        )

        if isinstance(market_df.columns, pd.MultiIndex):
            market_df.columns = market_df.columns.get_level_values(0)

        market_df = market_df.reset_index()

        ticker = yf.Ticker(symbol)
        actions = ticker.actions.copy()
        if actions is None or actions.empty:
            actions_df = pd.DataFrame(columns=["Date", "Dividends", "Stock Splits"])
        else:
            actions_df = actions.reset_index()

        return SourcePayload(market_data=market_df, corporate_actions=actions_df)
