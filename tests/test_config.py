from pathlib import Path

from marketguard.config import load_pipeline_config


def test_load_pipeline_config(tmp_path: Path) -> None:
    config_file = tmp_path / "pipeline.yaml"
    config_file.write_text(
        """
source:
  name: yahoo_finance
runtime:
  history_years: 3
  end_date: 2026-01-31
  request_sleep_seconds: 0
paths:
  universe_file: configs/security_universe.csv
  raw_data_dir: data/raw
  canonical_data_path: data/processed/canonical.parquet
  actions_data_path: data/processed/actions.parquet
  duckdb_path: data/processed/marketguard.duckdb
  run_metadata_dir: data/processed/run_metadata
  log_dir: logs
""".strip(),
        encoding="utf-8",
    )

    cfg = load_pipeline_config(config_file)

    assert cfg.source_name == "yahoo_finance"
    assert cfg.history_years == 3
    assert cfg.end_date == "2026-01-31"
    assert cfg.raw_data_dir == Path("data/raw")
