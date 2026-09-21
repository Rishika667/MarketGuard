from __future__ import annotations

from marketguard.adapters.base import BaseMarketDataAdapter
from marketguard.adapters.yahoo_finance import YahooFinanceAdapter


class AdapterFactoryError(ValueError):
    """Raised when an unknown data-source adapter is configured."""


def build_adapter(source_name: str, request_sleep_seconds: float = 0.0) -> BaseMarketDataAdapter:
    normalized = source_name.strip().lower()
    if normalized in {"yahoo", "yahoo_finance", "yfinance"}:
        return YahooFinanceAdapter(request_sleep_seconds=request_sleep_seconds)

    raise AdapterFactoryError(f"Unsupported source adapter: {source_name}")
