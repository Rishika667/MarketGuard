from pathlib import Path

import pandas as pd

from marketguard.storage import CanonicalStore


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "security_id": ["US0001", "US0001"],
            "symbol": ["AAPL", "AAPL"],
            "country": ["US", "US"],
            "market": ["US_EQUITY", "US_EQUITY"],
            "exchange": ["NASDAQ", "NASDAQ"],
            "currency": ["USD", "USD"],
            "observation_date": ["2026-01-01", "2026-01-02"],
            "open": [1.0, 2.0],
            "high": [1.1, 2.1],
            "low": [0.9, 1.9],
            "close": [1.05, 2.05],
            "adjusted_close": [1.05, 2.05],
            "volume": [100, 200],
            "source": ["yahoo_finance", "yahoo_finance"],
            "ingestion_timestamp": ["2026-01-03T00:00:00Z", "2026-01-03T00:00:00Z"],
            "run_id": ["run_a", "run_a"],
            "data_status": ["ok", "ok"],
        }
    )


def test_canonical_upsert_is_idempotent(tmp_path: Path) -> None:
    store = CanonicalStore(
        market_data_path=tmp_path / "canonical_market_data.parquet",
        actions_data_path=tmp_path / "canonical_actions.parquet",
        duckdb_path=tmp_path / "marketguard.duckdb",
    )

    first = _sample_df()
    second = _sample_df()

    df_after_first = store.upsert_market_data(first)
    df_after_second = store.upsert_market_data(second)

    assert len(df_after_first) == 2
    assert len(df_after_second) == 2
