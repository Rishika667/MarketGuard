import pandas as pd

from marketguard.normalization import normalize_market_data
from marketguard.validation import validate_canonical_market_data


def test_normalize_and_validate_market_data() -> None:
    raw = pd.DataFrame(
        {
            "Date": ["2026-01-02", "bad-date"],
            "Open": [100.0, 101.0],
            "High": [105.0, 99.0],
            "Low": [99.0, 98.0],
            "Close": [104.0, 97.0],
            "Adj Close": [103.5, 96.5],
            "Volume": [1000000, 900000],
        }
    )
    security = pd.Series(
        {
            "security_id": "US0001",
            "symbol": "AAPL",
            "market": "US_EQUITY",
            "exchange": "NASDAQ",
            "country": "US",
            "currency": "USD",
        }
    )

    normalized = normalize_market_data(raw, security, source="yahoo_finance", run_id="run_1")
    result = validate_canonical_market_data(normalized)

    assert not result.errors
    assert len(result.valid_data) == 1
    assert "Dropped 1 rows with invalid observation_date" in result.warnings
