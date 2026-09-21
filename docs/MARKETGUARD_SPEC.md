# MarketGuard — Project Specification

## Project

MarketGuard — Automated Market-Data Quality, Reconciliation & Exception Intelligence Platform

## Project Level

Intermediate portfolio project.

## Primary Domain

Financial Data / Market Data Operations / Data Quality

## Business Problem

Financial analysis and downstream decision-making depend on reliable market data.
Stale prices, invalid observations, missing records, corporate-action issues and
cross-source discrepancies can contaminate downstream analysis.

MarketGuard is designed to identify, evaluate and prioritize suspicious EOD
market-data records before they affect downstream users.

## Primary Users

- Market-data operations analyst
- Data-quality analyst
- Quantitative/research data consumer

## Operating Frequency

Daily EOD.

Real-time and tick-level infrastructure are outside the project scope.

## Target Universe

Approximately:

- 100 US equities
- 50 Indian equities

The exact universe-selection methodology may be determined during implementation,
provided it is documented and reproducible.

## Core Data

Where available:

- Date
- Open
- High
- Low
- Close
- Adjusted Close
- Volume
- Source
- Ingestion/freshness metadata
- Corporate-action/reference information

## Data Quality Dimensions

MarketGuard must evaluate:

1. Completeness
2. Validity
3. Consistency
4. Timeliness
5. Cross-source consistency

## QC Controls

The final implementation should contain approximately 10–12 explainable controls
covering:

- Invalid OHLC relationships
- Non-positive prices
- Missing observations
- Abnormal price movements
- Potential corporate-action anomalies
- Stale prices
- Cross-source discrepancies
- Missing trading days
- Volume anomalies
- Freshness/timeliness breaches
- Duplicate observations
- Adjusted/unadjusted inconsistencies where data permits

Exact thresholds and implementation methodology may be determined during
technical implementation.

## Exception Model

Exceptions should contain, where applicable:

- Security
- Date
- Rule
- Issue type
- Source
- Observed values
- Supporting evidence
- Severity
- DQ dimension
- Status
- Timestamp
- Resolution/override information

Expected lifecycle:

OPEN
→ INVESTIGATING
→ RESOLVED / OVERRIDDEN

## Data Quality Score

MarketGuard must calculate:

- Overall DQ score from 0–100
- Dimension-level DQ scores

The scoring methodology must be deterministic, reproducible and documented.

## Validation

Synthetic-error testing is mandatory.

The validation framework should inject controlled defects such as:

- stale prices
- missing records
- incorrect OHLC values
- artificial price movements
- cross-source discrepancies
- volume anomalies

Performance should be measured using appropriate metrics including:

- detection rate
- false-positive rate
- rule-level performance

## Dashboard

The final dashboard should contain four core views:

### 1. Control Room

- Overall DQ score
- Dimension scores
- Open exceptions
- Severity distribution
- Quality trends

### 2. Exception Queue

- Security
- Date
- Rule
- Severity
- Status
- DQ dimension
- Evidence
- Filters

### 3. Security Investigation

- Price history
- Source comparison
- Returns
- Volume
- Corporate-action evidence where available
- DQ history
- Exceptions

### 4. Source Reliability

Show observed source reliability using measures such as:

- Missing data
- Cross-source disagreement
- Freshness
- Rule failures

Do not represent source agreement as proof of absolute accuracy.

## Automated Reporting

The system should generate an automated quality report containing:

- Overall DQ score
- Dimension scores
- Exception counts
- Severity distribution
- Rule failures
- Source comparison
- Freshness status
- Significant quality changes

## Automation

Routine EOD execution should be automated.

Expected workflow:

EOD data
→ ingestion
→ normalization
→ QC
→ reconciliation
→ exceptions
→ DQ score
→ persistence
→ dashboard/report

## Technology Direction

Preferred lightweight technology includes:

- Python
- pandas
- NumPy
- DuckDB / Parquet
- Streamlit
- Plotly
- pytest
- GitHub

Implementation choices may be refined during development if justified.

## Data-Source Requirement

The portfolio implementation should not require paid institutional
market-data subscriptions.

Free, public or freemium sources are preferred.

The exact source combination should be selected during implementation based on:

- accessibility
- reproducibility
- coverage
- historical availability
- rate limits
- source terms

## Raw Data

Preserve raw source observations whenever practical before transformation.

## Explicitly Out of Scope

- Real-time streaming
- Tick-level systems
- ML anomaly detection
- LLM features
- Paid institutional feeds
- Large institutional universes
- Mobile applications
- Unnecessary microservices
- Unnecessary cloud infrastructure
- Trading signals
- Trading recommendations
- Automatic correction of ambiguous data
- Corporate-action prediction

## Required Final Deliverables

1. Automated EOD market-data pipeline
2. QC engine
3. Cross-source reconciliation
4. Exception management
5. DQ scoring
6. Streamlit dashboard
7. Synthetic-error validation
8. Automated quality report
9. Automated execution
10. Tests
11. Documentation
12. Production-gap / limitations documentation

## Production Gap

The final documentation should explain the difference between this portfolio
prototype and a production institutional market-data platform.

Potential future evolution includes:

- Licensed institutional feeds
- Larger security universe
- Intraday/real-time monitoring
- Formal vendor SLAs
- Advanced statistical or ML controls
- Enterprise infrastructure

These are future enhancements and are not part of the current implementation.
