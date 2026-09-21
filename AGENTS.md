# MarketGuard — AI Development Instructions

## 1. Project Purpose

MarketGuard is an intermediate-level portfolio project focused on automated
EOD market-data quality control, cross-source reconciliation, exception
management and data-quality intelligence.

The project is intended to demonstrate practical financial-data,
market-data-operations and data-quality engineering capability.

The authoritative project requirements are defined in:

docs/MARKETGUARD_SPEC.md

Do not contradict or silently expand those requirements.

---

## 2. Source of Truth

Before making changes:

1. Read this file.
2. Read docs/MARKETGUARD_SPEC.md.
3. Read docs/PROJECT_STATUS.md.
4. Inspect the existing repository and implementation.
5. Continue from the existing state rather than rebuilding completed work.

The repository is the source of truth for project state.

---

## 3. Core Development Principles

Prioritize:

1. Correctness
2. Explainability
3. Reproducibility
4. Maintainability
5. Testability
6. Business usefulness
7. Appropriate simplicity

Do not add complexity merely to make the project appear more advanced.

---

## 4. Project Scope

MarketGuard is an EOD market-data quality and reconciliation platform.

The project includes:

- Automated EOD data ingestion
- Data normalization
- Market-data quality controls
- Cross-source reconciliation
- Exception generation
- Exception investigation workflow
- Data-quality scoring
- Synthetic-error validation
- Dashboarding
- Automated quality reporting
- Automated execution
- Testing
- Documentation

---

## 5. Explicitly Out of Scope

Do not implement the following unless explicitly approved:

- Real-time market-data streaming
- Tick-level infrastructure
- ML anomaly detection
- LLM features
- Paid institutional market-data feeds
- Large institutional-scale universes
- Mobile applications
- Unnecessary microservices
- Kubernetes or unnecessary cloud infrastructure
- Trading recommendations
- Trading signals
- Automatic correction of ambiguous market data
- Corporate-action prediction

If an idea is useful but outside the scope, document it under future enhancements instead of implementing it.

---

## 6. Automation

The routine project workflow should be automated.

The expected operating model is:

EOD data availability
→ ingestion
→ normalization
→ quality controls
→ reconciliation
→ exception generation
→ DQ scoring
→ persistence
→ dashboard/report update

Human intervention should primarily be required for ambiguous exception investigation,
resolution and overrides.

---

## 7. Explainability

Every material exception must explain why it was generated.

Prefer:

Rule
→ Evidence
→ Severity
→ Exception
→ Investigation
→ Resolution

over opaque anomaly flags.

---

## 8. Data Safety

Preserve raw source data whenever practical before transformation.

Do not silently overwrite source data.

Maintain sufficient metadata to understand:

- source
- ingestion time
- observation date
- transformation
- quality result

---

## 9. Testing

Testing is mandatory.

Before declaring a component complete:

- run relevant automated tests
- verify expected behavior
- test important edge cases
- document known limitations

Synthetic-error testing must be used to evaluate the QC framework.

Where practical, measure:

- detection rate
- false-positive rate
- rule-level performance

---

## 10. Documentation

When implementation changes materially:

- update relevant documentation
- update docs/PROJECT_STATUS.md
- update docs/CHANGELOG.md when appropriate

Do not leave important architectural or implementation decisions undocumented.

---

## 11. Session / Credit Safety

The project must remain resumable if an AI session ends unexpectedly
or available AI credits are exhausted.

At the end of every substantial development task:

1. Save all completed work to the repository.
2. Run relevant tests.
3. Update docs/PROJECT_STATUS.md.
4. Record incomplete work.
5. Record known issues.
6. Record the exact next recommended action.
7. Commit completed work to Git.

Never leave completed work only in the AI conversation.

---

## 12. Existing Work Protection

Before modifying an existing component:

- inspect the current implementation
- understand its purpose
- avoid unnecessary rewrites
- preserve working functionality
- modify only what is required

Do not rebuild functioning components simply because another implementation is possible.

---

## 13. Scope Control

Do not expand the project scope without explicit approval.

If implementation reveals a potentially valuable additional feature:

1. document the idea
2. explain why it may be useful
3. place it under future enhancements
4. do not implement it automatically

---

## 14. Completion Standard

A task is not complete merely because code has been written.

A component should be considered complete only when:

- implementation exists
- relevant tests pass
- documentation is updated
- project status is updated
- known limitations are documented
- the repository remains usable

---

## 15. Stop Condition

When the requested task is complete and acceptance criteria are satisfied:

STOP.

Do not continue adding unrelated features.

Do not use additional effort for unnecessary enhancements.
