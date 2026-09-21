# MarketGuard

Automated market-data quality, reconciliation and exception-intelligence platform for EOD financial market data.

## Stage 1 (Implemented)

Stage 1 delivers the MarketGuard ingestion foundation:

- Reproducible security universe (~150 securities: 100 US + 50 IN)
- Config-driven EOD ingestion pipeline
- Source-adapter architecture (Yahoo Finance adapter implemented)
- Raw immutable snapshot storage (Parquet)
- Canonical normalized dataset generation (Parquet)
- Corporate-actions ingestion (dividends/splits where available)
- DuckDB analytical persistence
- Structured logging and run metadata
- Basic ingestion-time structural validation (pre-QC)
- Rerunnable/idempotent canonical upserts
- Automated tests for core Stage 1 components

## Repository Layout

- `configs/pipeline.yaml` — Stage 1 runtime/source/path configuration
- `configs/security_universe.csv` — reproducible 150-security universe
- `src/marketguard/` — pipeline, adapters, normalization, validation, storage
- `tests/` — unit/integration-style tests (mocked source for repeatability)
- `docs/` — specification, architecture, status, changelog, dictionary

## Data Source Implemented

- `yahoo_finance` (`yfinance`) for EOD OHLCV and corporate actions

## Quick Start

```bash
python -m pip install -r requirements.txt
PYTHONPATH=src python -m marketguard.pipeline.eod_ingestion --config configs/pipeline.yaml
```

## Test Command

```bash
pytest -q
```

## Stage 1 Output Artifacts

- Raw market snapshots: `data/raw/yahoo_finance/market_data/run_<run_id>.parquet`
- Raw corporate actions: `data/raw/yahoo_finance/corporate_actions/run_<run_id>.parquet`
- Canonical market data: `data/processed/canonical/canonical_market_data.parquet`
- Canonical corporate actions: `data/processed/canonical/canonical_corporate_actions.parquet`
- DuckDB: `data/processed/marketguard.duckdb`
- Run metadata: `data/processed/run_metadata/run_<run_id>.json`
- Logs: `logs/marketguard_pipeline.log`

## Notes

- No secrets are committed.
- Pipeline source/auth can be swapped later by implementing additional adapters and updating config.
- Stage 2 will build on Stage 1 canonical outputs for QC/scoring/exception intelligence.
