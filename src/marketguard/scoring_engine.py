from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

import pandas as pd

from marketguard.qc_engine import RULE_CATALOG

DIMENSION_DEFAULT_WEIGHTS = {
    "completeness": 0.2,
    "validity": 0.25,
    "consistency": 0.2,
    "timeliness": 0.2,
    "cross_source_consistency": 0.15,
}

DIMENSION_PENALTY_MULTIPLIER = {
    "completeness": 1.2,
    "validity": 1.4,
    "consistency": 1.1,
    "timeliness": 1.0,
    "cross_source_consistency": 1.3,
}


@dataclass
class ScoreResult:
    overall_score: float
    dimension_scores: pd.DataFrame


def calculate_dq_scores(
    market_data: pd.DataFrame,
    exceptions: pd.DataFrame,
    weights: dict[str, float] | None = None,
) -> ScoreResult:
    """Calculate deterministic overall and dimension-level DQ scores (0-100)."""
    if market_data.empty:
        empty = pd.DataFrame(columns=["dq_dimension", "total_records", "violations", "violation_rate", "dimension_score"])
        return ScoreResult(overall_score=0.0, dimension_scores=empty)

    weights = {**DIMENSION_DEFAULT_WEIGHTS, **(weights or {})}

    total_records = len(market_data)

    exceptions_by_dimension = {}
    if not exceptions.empty:
        exceptions_by_dimension = (
            exceptions.groupby("dq_dimension")["exception_id"].nunique().to_dict()
        )

    rows: list[dict] = []
    for dim in DIMENSION_DEFAULT_WEIGHTS:
        violations = int(exceptions_by_dimension.get(dim, 0))
        violation_rate = violations / max(total_records, 1)
        multiplier = DIMENSION_PENALTY_MULTIPLIER.get(dim, 1.0)
        dimension_score = max(0.0, 100.0 * (1.0 - (violation_rate * multiplier)))
        rows.append(
            {
                "dq_dimension": dim,
                "total_records": total_records,
                "violations": violations,
                "violation_rate": violation_rate,
                "dimension_score": round(dimension_score, 4),
                "weight": weights[dim],
            }
        )

    dimension_scores = pd.DataFrame(rows)
    overall_score = float((dimension_scores["dimension_score"] * dimension_scores["weight"]).sum())

    dimension_scores["scored_at"] = datetime.now(UTC)

    return ScoreResult(overall_score=round(overall_score, 4), dimension_scores=dimension_scores)


def build_rule_summary(exceptions: pd.DataFrame) -> pd.DataFrame:
    """Summarize exception counts by rule with dimension mapping."""
    if exceptions.empty:
        return pd.DataFrame(columns=["rule_id", "rule_name", "dq_dimension", "exception_count"])

    summary = (
        exceptions.groupby(["rule_id", "rule_name", "dq_dimension"], as_index=False)
        .size()
        .rename(columns={"size": "exception_count"})
    )

    all_rules = []
    for rid, meta in RULE_CATALOG.items():
        all_rules.append({"rule_id": rid, "rule_name": meta["name"], "dq_dimension": meta["dimension"]})

    rule_catalog_df = pd.DataFrame(all_rules)
    merged = rule_catalog_df.merge(summary, on=["rule_id", "rule_name", "dq_dimension"], how="left")
    merged["exception_count"] = merged["exception_count"].fillna(0).astype(int)

    return merged.sort_values("rule_id").reset_index(drop=True)
