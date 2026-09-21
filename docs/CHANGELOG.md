# MarketGuard — Changelog

## 2026-09-21

### Added

- Stage 1 implementation package under `src/marketguard/`
  - config loader
  - security-universe loader
  - adapter abstraction
  - Yahoo Finance adapter
  - normalization layer
  - ingestion pre-QC validation
  - raw/canonical/metadata persistence
  - pipeline entrypoint
- Reproducible universe file `configs/security_universe.csv` (150 securities)
- Stage 1 configuration file `configs/pipeline.yaml`
- Canonical + corporate-action schema implementation
- DuckDB canonical table refresh integration
- Structured JSON logging output
- Run metadata output per ingestion run
- Test suite for Stage 1 core behavior under `tests/`

### Changed

- Updated `requirements.txt` with runtime/test dependencies
- Updated `README.md` with Stage 1 run/test usage and outputs
- Updated `docs/ARCHITECTURE.md` and `docs/DATA_DICTIONARY.md` to implemented state
- Updated `docs/PROJECT_STATUS.md` to reflect Stage 1 completion

### Verified

- `pytest -q` → **5 passed**
- Live pipeline run completed with partial-success handling for symbol-level source issues

### Notes

- Source-level occasional empty payloads are surfaced as explicit run failures in metadata/logs (not silently masked).
