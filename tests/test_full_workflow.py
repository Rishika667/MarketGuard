from pathlib import Path

import pandas as pd

from marketguard.pipeline.run_marketguard import run_marketguard


def test_full_marketguard_workflow_without_live_ingestion(tmp_path: Path) -> None:
    canonical_path = tmp_path / "canonical_market_data.parquet"
    actions_path = tmp_path / "canonical_actions.parquet"

    market_rows = []
    for i, d in enumerate(pd.date_range("2026-01-01", periods=45, freq="B")):
        market_rows.append(
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
    pd.DataFrame(market_rows).to_parquet(canonical_path, index=False)
    pd.DataFrame(columns=["security_id", "symbol", "observation_date", "dividend", "stock_split", "source"]).to_parquet(actions_path, index=False)

    universe_file = tmp_path / "universe.csv"
    universe_file.write_text(
        "security_id,symbol,yahoo_symbol,market,exchange,country,currency,is_active\nUS0001,AAPL,AAPL,US_EQUITY,NASDAQ,US,USD,True\n",
        encoding="utf-8",
    )

    cfg = tmp_path / "pipeline.yaml"
    cfg.write_text(
        f"""
source:
  name: yahoo_finance
runtime:
  history_years: 1
  end_date: 2026-02-01
  request_sleep_seconds: 0
paths:
  universe_file: {universe_file}
  raw_data_dir: {tmp_path / 'raw'}
  canonical_data_path: {canonical_path}
  actions_data_path: {actions_path}
  duckdb_path: {tmp_path / 'marketguard.duckdb'}
  run_metadata_dir: {tmp_path / 'run_metadata'}
  log_dir: {tmp_path / 'logs'}
""".strip(),
        encoding="utf-8",
    )

    result = run_marketguard(config_path=cfg, run_ingestion=False, run_synthetic=True)

    assert result["overall_dq_score"] >= 0
    assert result["paths"]["exceptions"].endswith("exceptions.parquet")
    assert Path(result["paths"]["report"]).exists()
