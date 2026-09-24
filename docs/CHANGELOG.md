# MarketGuard — Changelog

## 2026-09-22

### Added

- Full QC engine (`src/marketguard/qc_engine.py`) implementing R01–R12
- Exception lifecycle management (`src/marketguard/exception_manager.py`)
- DQ scoring module (`src/marketguard/scoring_engine.py`)
- Synthetic defect-injection validation (`src/marketguard/synthetic_validation.py`)
- Automated markdown quality reporting (`src/marketguard/reporting.py`)
- Dashboard dataset preparation (`src/marketguard/dashboard_prep.py`)
- End-to-end orchestration command (`src/marketguard/pipeline/run_marketguard.py`)
- GitHub Actions workflow for tests + scheduled/manual runs (`.github/workflows/marketguard_eod.yml`)
- Expanded tests for QC/exceptions/scoring/synthetic/full workflow

### Changed

- Updated README to reflect full executable workflow beyond ingestion foundation
- Updated architecture, QC rules, data dictionary, and project status documentation

### Verified

- `pytest -q` → **9 passed**
- `PYTHONPATH=src python -m marketguard.pipeline.run_marketguard --config configs/pipeline.yaml` executed successfully on canonical data

## 2026-09-21

### Added

- Stage 1 ingestion foundation package under `src/marketguard/`
- Reproducible universe file `configs/security_universe.csv` (150 securities)
- Stage 1 runtime config `configs/pipeline.yaml`
- Canonical + corporate-action ingestion and persistence outputs
- Ingestion run metadata and structured logs
- Initial Stage 1 test suite
