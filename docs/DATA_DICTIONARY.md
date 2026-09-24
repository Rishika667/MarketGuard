# MarketGuard — Data Dictionary

## Status

Canonical ingestion + QC + exceptions + scoring + dashboard output schemas implemented.

## 1) Canonical Market Data (`data/processed/canonical/canonical_market_data.parquet`)

| Field | Type | Description |
|---|---|---|
| security_id | string | Internal MarketGuard security identifier |
| symbol | string | Ticker symbol |
| country | string | Country code (`US` / `IN`) |
| market | string | Market segment label |
| exchange | string | Exchange code/name |
| currency | string | Trading currency |
| observation_date | date | EOD observation date |
| open | float | Open price |
| high | float | High price |
| low | float | Low price |
| close | float | Close price |
| adjusted_close | float nullable | Adjusted close where available |
| volume | float | Volume |
| source | string | Source identifier |
| ingestion_timestamp | timestamp (UTC) | Ingestion processing timestamp |
| run_id | string | Ingestion run identifier |
| data_status | string | Basic availability marker |

## 2) Canonical Corporate Actions (`data/processed/canonical/canonical_corporate_actions.parquet`)

| Field | Type | Description |
|---|---|---|
| security_id | string | Internal security identifier |
| symbol | string | Ticker symbol |
| observation_date | date | Action date |
| dividend | float | Dividend amount |
| stock_split | float | Split field from source |
| country | string | Country |
| market | string | Market segment |
| exchange | string | Exchange |
| currency | string | Currency |
| source | string | Source identifier |
| ingestion_timestamp | timestamp (UTC) | Processing timestamp |
| run_id | string | Ingestion run ID |

## 3) Exceptions (`data/processed/quality/exceptions.parquet`)

| Field | Type | Description |
|---|---|---|
| exception_id | string | Deterministic exception key |
| quality_run_id | string | Quality run identifier |
| rule_id | string | Rule code (`R01`...`R12`) |
| rule_name | string | Rule label |
| issue_type | string | Issue category |
| dq_dimension | string | DQ dimension |
| severity | string | HIGH / MEDIUM / LOW |
| status | string | OPEN / INVESTIGATING / RESOLVED / OVERRIDDEN |
| owner | string | Assigned analyst or UNASSIGNED |
| security_id | string | Security identifier |
| symbol | string | Symbol |
| country | string | Country |
| market | string | Market |
| exchange | string | Exchange |
| currency | string | Currency |
| observation_date | date | Impacted date |
| source | string | Source |
| evidence | string (JSON) | Rule-specific evidence payload |
| created_at | timestamp (UTC) | Exception creation timestamp |

## 4) Exception Ledger (`data/processed/quality/exception_ledger.parquet`)

Adds lifecycle update tracking fields such as `updated_at` and `resolution_note` while preserving current status.

## 5) Scoring Outputs (`data/processed/quality/`)

- `dimension_scores.parquet`: dimension-level violation counts/rates and score values
- `overall_score.parquet`: overall weighted DQ score
- `rule_summary.parquet`: per-rule exception counts
- `qc_metrics.parquet`: exception counts by rule and severity

## 6) Synthetic Validation Outputs

- `synthetic_validation_metrics.parquet`: per-rule injected count, detected count, detection rate, false-positive rate

## 7) Dashboard Datasets (`data/processed/dashboard/`)

- `control_room.parquet`
- `dimension_scores.parquet`
- `exceptions_queue.parquet`
- `security_investigation.parquet`
- `source_reliability.parquet`
- `rule_summary.parquet`

## Raw Snapshot Metadata Columns

Raw snapshots preserve at least:
- `source`
- `source_symbol`
- `security_id`
- `symbol`
- `run_id`
- `retrieved_at`
