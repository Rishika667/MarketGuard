# MarketGuard — QC Rules

## Status

QC rules are defined conceptually in the project specification.

Exact thresholds and implementation methodology are pending technical
design and validation.

## Required Rule Coverage

1. Invalid OHLC
2. Non-positive price
3. Missing observation
4. Abnormal price movement
5. Potential corporate-action anomaly
6. Stale price
7. Cross-source discrepancy
8. Missing trading day
9. Volume anomaly
10. Freshness breach
11. Duplicate observation
12. Adjusted/unadjusted inconsistency

## Rule Design Principle

Each rule should be:

- Explainable
- Deterministic where appropriate
- Testable
- Documented
- Validated using controlled errors where practical

## Rule Documentation Requirement

Each implemented rule should document:

- Rule ID
- Rule name
- Purpose
- Logic
- Required inputs
- Thresholds
- DQ dimension
- Severity logic
- Evidence generated
- Known limitations
- Validation results
