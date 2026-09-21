from pathlib import Path

import pandas as pd

from marketguard.adapters.base import SourcePayload
from marketguard.pipeline import eod_ingestion


class DummyAdapter:
    def fetch_security_data(self, symbol, start_date, end_date):
        market_data = pd.DataFrame(
            {
                "Date": ["2026-01-01", "2026-01-02"],
                "Open": [10.0, 10.5],
                "High": [11.0, 11.5],
                "Low": [9.5, 10.0],
                "Close": [10.8, 11.2],
                "Adj Close": [10.8, 11.2],
                "Volume": [1000, 1200],
            }
        )
        actions = pd.DataFrame({"Date": ["2026-01-02"], "Dividends": [0.2], "Stock Splits": [0.0]})
        return SourcePayload(market_data=market_data, corporate_actions=actions)


def test_pipeline_runs_and_is_rerunnable(tmp_path: Path, monkeypatch) -> None:
    universe_file = tmp_path / "universe.csv"
    universe_file.write_text(
        """security_id,symbol,yahoo_symbol,market,exchange,country,currency,is_active
US0001,AAPL,AAPL,US_EQUITY,NASDAQ,US,USD,True
US0002,MSFT,MSFT,US_EQUITY,NASDAQ,US,USD,True
""",
        encoding="utf-8",
    )

    config_file = tmp_path / "pipeline.yaml"
    config_file.write_text(
        f"""
source:
  name: yahoo_finance
runtime:
  history_years: 1
  end_date: 2026-01-31
  request_sleep_seconds: 0
paths:
  universe_file: {universe_file}
  raw_data_dir: {tmp_path / 'raw'}
  canonical_data_path: {tmp_path / 'processed' / 'canonical_market_data.parquet'}
  actions_data_path: {tmp_path / 'processed' / 'canonical_actions.parquet'}
  duckdb_path: {tmp_path / 'processed' / 'marketguard.duckdb'}
  run_metadata_dir: {tmp_path / 'processed' / 'run_metadata'}
  log_dir: {tmp_path / 'logs'}
""".strip(),
        encoding="utf-8",
    )

    monkeypatch.setattr(eod_ingestion, "build_adapter", lambda *_args, **_kwargs: DummyAdapter())

    first = eod_ingestion.run_pipeline(config_file)
    second = eod_ingestion.run_pipeline(config_file)

    canonical = pd.read_parquet(tmp_path / "processed" / "canonical_market_data.parquet")
    assert first["status"] == "success"
    assert second["status"] == "success"
    assert len(canonical) == 4
