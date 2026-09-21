# MarketGuard — Architecture

## Current Stage

Stage 1 — Foundation + Automated Market-Data Pipeline

## Stage 1 Implemented Flow

Configured EOD source
→ source adapter
→ raw immutable snapshots (Parquet)
→ normalization
→ ingestion-time pre-QC structural validation
→ canonical upsert (Parquet)
→ DuckDB refresh
→ run metadata + structured logs

## Stage 1 Components

### 1) Configuration Layer
- `configs/pipeline.yaml`
- Loaded by `src/marketguard/config.py`
- Controls source, paths, and runtime window parameters

### 2) Security Universe
- `configs/security_universe.csv`
- 150 active equities (100 US, 50 India)
- Loaded/validated by `src/marketguard/universe.py`

### 3) Source Adapter Layer
- Interface: `src/marketguard/adapters/base.py`
- Factory: `src/marketguard/adapters/factory.py`
- Implemented adapter: `src/marketguard/adapters/yahoo_finance.py`

### 4) Normalization Layer
- `src/marketguard/normalization.py`
- Converts source payload to canonical market and corporate-action schemas

### 5) Pre-QC Ingestion Validation
- `src/marketguard/validation.py`
- Checks required fields, date validity, numeric OHLC, OHLC sanity, non-positive price rows, duplicate keys

### 6) Persistence Layer
- `src/marketguard/storage.py`
- Raw snapshots (immutable run files)
- Canonical upsert with rerun-safe deduplication
- DuckDB tables: `canonical_market_data`, `canonical_corporate_actions`
- Run metadata JSON persistence

### 7) Pipeline Entrypoint
- `src/marketguard/pipeline/eod_ingestion.py`
- Runnable command:
  - `PYTHONPATH=src python -m marketguard.pipeline.eod_ingestion --config configs/pipeline.yaml`

## Storage Strategy (Stage 1)

- Raw source snapshots: Parquet
- Canonical datasets: Parquet
- Analytical querying layer: DuckDB
- Metadata/audit trail (run-level): JSON

## Scope Boundary

Stage 1 intentionally excludes:
- Full QC rule engine
- Exception lifecycle workflow
- DQ scoring model
- Synthetic error framework
- Dashboard/reporting layer

These are planned for Stage 2+ and consume Stage 1 canonical outputs.
