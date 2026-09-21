# MarketGuard — Data Dictionary

## Status

Stage 1 canonical schema implemented.

## Canonical Market Data (`canonical_market_data.parquet`)

| Field | Type | Description |
|---|---|---|
| security_id | string | Internal MarketGuard security identifier |
| symbol | string | Human-readable ticker symbol |
| country | string | Country code (`US` / `IN`) |
| market | string | Market segment label (`US_EQUITY` / `IN_EQUITY`) |
| exchange | string | Exchange name/code |
| currency | string | Trading currency (`USD` / `INR`) |
| observation_date | date | EOD observation date |
| open | float | Opening price |
| high | float | High price |
| low | float | Low price |
| close | float | Closing price |
| adjusted_close | float nullable | Adjusted close where source provides it |
| volume | float | Traded volume |
| source | string | Data source identifier (`yahoo_finance`) |
| ingestion_timestamp | timestamp (UTC) | Ingestion processing timestamp |
| run_id | string | Ingestion run identifier |
| data_status | string | Basic availability marker (`ok`, `missing_adjusted_close`) |

## Canonical Corporate Actions (`canonical_corporate_actions.parquet`)

| Field | Type | Description |
|---|---|---|
| security_id | string | Internal security identifier |
| symbol | string | Ticker symbol |
| observation_date | date | Corporate-action effective date |
| dividend | float | Cash dividend amount (0 when absent) |
| stock_split | float | Split factor field from source (0 when absent) |
| country | string | Country code |
| market | string | Market segment |
| exchange | string | Exchange |
| currency | string | Currency |
| source | string | Data source identifier |
| ingestion_timestamp | timestamp (UTC) | Ingestion processing timestamp |
| run_id | string | Ingestion run identifier |

## Raw Snapshot Metadata Columns (Stored with source payload)

- `source`
- `source_symbol`
- `security_id`
- `symbol`
- `run_id`
- `retrieved_at`

These preserve source-observed payload lineage for run-level investigations.
