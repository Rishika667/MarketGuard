import pandas as pd

from marketguard.qc_engine import run_quality_controls


def _sample_market_data() -> pd.DataFrame:
    rows = []
    for i, d in enumerate(pd.date_range("2026-01-01", periods=35, freq="B")):
        rows.append(
            {
                "security_id": "US0001",
                "symbol": "AAPL",
                "country": "US",
                "market": "US_EQUITY",
                "exchange": "NASDAQ",
                "currency": "USD",
                "observation_date": d.date(),
                "open": 100 + i,
                "high": 101 + i,
                "low": 99 + i,
                "close": 100 + i,
                "adjusted_close": 100 + i,
                "volume": 100000 + i,
                "source": "yahoo_finance",
                "ingestion_timestamp": "2026-02-01T00:00:00Z",
                "run_id": "run",
                "data_status": "ok",
            }
        )
    return pd.DataFrame(rows)


def test_qc_engine_detects_multiple_rules() -> None:
    df = _sample_market_data()

    # Inject known defects
    df.loc[5, "close"] = -10  # R02
    df.loc[10, "high"] = df.loc[10, "low"] - 1  # R01
    dup = df.iloc[[12]].copy()
    df = pd.concat([df, dup], ignore_index=True)  # R11

    result = run_quality_controls(df, corporate_actions=pd.DataFrame(), run_id="qrun")

    assert not result.exceptions.empty
    assert {"R01", "R02", "R11"}.issubset(set(result.exceptions["rule_id"]))
    assert (result.exceptions["status"] == "OPEN").all()
