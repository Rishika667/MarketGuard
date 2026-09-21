# MarketGuard — Architecture

## Status

To be finalized during the technical design / implementation stage.

## Target Logical Flow

EOD market-data sources
→ ingestion
→ raw data
→ normalization
→ canonical data
→ quality controls
→ reconciliation
→ evidence
→ severity
→ exceptions
→ DQ scoring
→ persistence
→ dashboard/reporting

## Technical Decisions Pending

- Exact data sources
- Exact storage implementation
- Exact ingestion architecture
- Exact normalization approach
- Exact scheduling mechanism
- Exact repository implementation structure
- Exact deployment approach

These decisions should be based on reproducibility, reliability,
simplicity, cost and portfolio credibility.

Do not prematurely introduce unnecessary production infrastructure.
