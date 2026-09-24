# MarketGuard — QC Rules

## Status

Implemented (R01–R12) in `src/marketguard/qc_engine.py`.

## Rule Coverage

| Rule ID | Rule | Dimension | Implemented Logic (Summary) |
|---|---|---|---|
| R01 | Invalid OHLC | validity | Flags rows where OHLC relationships are structurally impossible |
| R02 | Non-positive price | validity | Flags rows with open/high/low/close <= 0 |
| R03 | Missing required observation | completeness | Flags security dates missing vs market-level observed trading dates |
| R04 | Extreme return anomaly | validity | Flags returns breaching absolute threshold and volatility-scaled threshold |
| R05 | Potential corporate-action anomaly | consistency | Flags large return jumps without same-day split/dividend evidence |
| R06 | Stale price | timeliness | Flags repeated close streaks >= configured stale-day threshold |
| R07 | Cross-source price break | cross_source_consistency | Flags large close-price divergence across sources (when multi-source data exists) |
| R08 | Missing trading day | completeness | Flags unusually large business-day gaps between observations |
| R09 | Volume anomaly | consistency | Flags extreme volume z-scores vs rolling history |
| R10 | Freshness breach | timeliness | Flags securities lagging global latest observation by configured business-day threshold |
| R11 | Duplicate observation | consistency | Flags duplicate (security_id, observation_date, source) records |
| R12 | Adjusted/unadjusted inconsistency | consistency | Flags large adjusted-vs-close divergence absent same-day action evidence |

## Severity Logic

- High-severity by default: R01, R02, R11
- Other rules use magnitude-based severity bands:
  - HIGH: magnitude >= 0.5
  - MEDIUM: magnitude >= 0.2
  - LOW: otherwise

## Evidence Model

Each exception carries serialized evidence fields relevant to the triggered rule (e.g., return, rolling volatility, business-gap, close pair, etc.) plus security/date/source identifiers.

## Configuration

Rule parameters currently use defaults in code (`DEFAULT_QC_PARAMS`), including thresholds for return, stale days, cross-source divergence, freshness lag, and adjusted-close discrepancy.

## Limitation Notes

- R07 produces outputs only when canonical dataset includes >=2 sources for same security/date.
- Corporate-action corroboration is evidence-based and does not automatically confirm true corporate-action events.
