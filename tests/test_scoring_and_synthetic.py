import pandas as pd

from marketguard.qc_engine import run_quality_controls
from marketguard.scoring_engine import calculate_dq_scores
from marketguard.synthetic_validation import run_synthetic_validation


def _market_data() -> pd.DataFrame:
    rows = []
    for i, d in enumerate(pd.date_range("2026-01-01", periods=50, freq="B")):
        rows.append(
            {
                "security_id": "US0001",
                "symbol": "AAPL",
                "country": "US",
                "market": "US_EQUITY",
                "exchange": "NASDAQ",
                "currency": "USD",
                "observation_date": d.date(),
                "open": 100 + i * 0.1,
                "high": 101 + i * 0.1,
                "low": 99 + i * 0.1,
                "close": 100 + i * 0.1,
                "adjusted_close": 100 + i * 0.1,
                "volume": 100000 + i * 100,
                "source": "yahoo_finance",
                "ingestion_timestamp": "2026-02-01T00:00:00Z",
                "run_id": "run",
                "data_status": "ok",
            }
        )
    return pd.DataFrame(rows)


def test_scoring_and_synthetic_validation() -> None:
    market_data = _market_data()
    qc = run_quality_controls(market_data, corporate_actions=pd.DataFrame(), run_id="quality_1")

    scores = calculate_dq_scores(market_data, qc.exceptions)
    assert 0 <= scores.overall_score <= 100
    assert len(scores.dimension_scores) == 5

    synthetic = run_synthetic_validation(market_data, pd.DataFrame(), run_id="quality_1")
    assert not synthetic.detection_metrics.empty
    assert synthetic.detection_metrics["detection_rate"].between(0, 1).all()
