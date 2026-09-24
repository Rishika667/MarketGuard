from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date

import pandas as pd


@dataclass
class SourcePayload:
    market_data: pd.DataFrame
    corporate_actions: pd.DataFrame


class BaseMarketDataAdapter(ABC):
    """Contract for source-specific market-data adapters."""

    source_name: str

    @abstractmethod
    def fetch_security_data(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
    ) -> SourcePayload:
        """Fetch EOD OHLCV and corporate-action data for a symbol."""

