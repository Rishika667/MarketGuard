# MarketGuard — Architecture

## Current Implementation Status

Foundation + QC + Exceptions + DQ Scoring + Synthetic Validation + Reporting + Dashboard Data Prep

## End-to-End Flow

Configured source(s)
→ ingestion adapters
→ raw immutable snapshots
→ normalization
→ canonical market/corporate-action datasets
→ QC engine (R01-R12)
→ severity/evidence
→ exceptions + lifecycle ledger
→ DQ scoring (overall + dimensions)
→ synthetic validation
→ automated quality report
→ dashboard-ready datasets

## Implemented Modules

### Ingestion Foundation
- `src/marketguard/config.py`
- `src/marketguard/universe.py`
- `src/marketguard/adapters/base.py`
- `src/marketguard/adapters/yahoo_finance.py`
- `src/marketguard/normalization.py`
- `src/marketguard/validation.py`
- `src/marketguard/storage.py`
- `src/marketguard/pipeline/eod_ingestion.py`

### Quality / Exceptions / Scoring
- `src/marketguard/qc_engine.py` (rules R01–R12)
- `src/marketguard/exception_manager.py` (OPEN/INVESTIGATING/RESOLVED/OVERRIDDEN ledger)
- `src/marketguard/scoring_engine.py` (0–100 overall + 5 dimensions)
- `src/marketguard/synthetic_validation.py` (controlled defect injection + detection metrics)

### Reporting / Dashboard Outputs
- `src/marketguard/reporting.py` (automated markdown quality report)
- `src/marketguard/dashboard_prep.py` (dashboard parquet datasets)
- `src/marketguard/pipeline/run_marketguard.py` (full orchestration)

## Persistence

- Raw snapshots: `data/raw/`
- Canonical datasets: `data/processed/canonical/`
- QC/scoring outputs: `data/processed/quality/`
- Dashboard datasets: `data/processed/dashboard/`
- Reports: `reports/generated/`
- Analytical DB: `data/processed/marketguard.duckdb`

## Automation

- CLI full run:
  - `PYTHONPATH=src python -m marketguard.pipeline.run_marketguard --config configs/pipeline.yaml [--run-ingestion]`
- GitHub Actions workflow:
  - `.github/workflows/marketguard_eod.yml`
  - Includes test job + schedule/dispatch MarketGuard run job

## Design Notes

- Source reliability metrics represent observed behavior, not proof of absolute correctness.
- Architecture keeps provider retrieval isolated from normalization/QC/scoring/reporting layers.
