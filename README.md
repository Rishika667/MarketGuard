# MarketGuard

Automated EOD market-data quality, reconciliation, exception-intelligence, and scoring platform.

## Implemented Capabilities

- Reproducible 150-security universe (`100 US + 50 IN`)
- Config-driven EOD ingestion with source-adapter architecture
- Raw immutable snapshots + canonical normalized datasets (Parquet)
- Corporate-action ingestion (dividends/splits where available)
- Ingestion-time structural pre-QC validation
- Full QC rule engine (R01–R12)
- Exception generation with evidence, severity, and lifecycle ledger
- Deterministic DQ scoring (overall + 5 dimensions)
- Synthetic-error validation with rule-level detection metrics
- Automated quality report generation (Markdown)
- Dashboard-ready dataset generation (Parquet views)
- DuckDB analytical table refresh
- Scheduled/dispatch automation via GitHub Actions

## Data Source

- `yahoo_finance` (`yfinance`) for EOD OHLCV and corporate actions

## Core Commands

Install:

```bash
python -m pip install -r requirements.txt
```

Run ingestion only:

```bash
PYTHONPATH=src python -m marketguard.pipeline.eod_ingestion --config configs/pipeline.yaml
```

Run full workflow (canonical data -> QC -> exceptions -> scoring -> report -> dashboard data):

```bash
PYTHONPATH=src python -m marketguard.pipeline.run_marketguard --config configs/pipeline.yaml
```

Run full workflow with fresh ingestion first:

```bash
PYTHONPATH=src python -m marketguard.pipeline.run_marketguard --config configs/pipeline.yaml --run-ingestion
```

Run tests:

```bash
pytest -q
```

## Main Output Artifacts

- Raw snapshots: `data/raw/yahoo_finance/...`
- Canonical market data: `data/processed/canonical/canonical_market_data.parquet`
- Canonical corporate actions: `data/processed/canonical/canonical_corporate_actions.parquet`
- QC exceptions + metrics + scores: `data/processed/quality/`
- Dashboard datasets: `data/processed/dashboard/`
- Quality report: `reports/generated/quality_report_<quality_run_id>.md`
- DuckDB: `data/processed/marketguard.duckdb`

## Notes

- Use outputs as **observed source reliability** signals, not proof of absolute correctness.
- No secrets are committed.
