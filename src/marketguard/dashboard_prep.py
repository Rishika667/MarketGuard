from __future__ import annotations

from pathlib import Path

import pandas as pd


def build_dashboard_datasets(
    output_dir: str | Path,
    market_data: pd.DataFrame,
    exceptions: pd.DataFrame,
    dimension_scores: pd.DataFrame,
    overall_score: float,
    rule_summary: pd.DataFrame,
) -> dict[str, str]:
    """Prepare dashboard-ready parquet datasets from computed outputs."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    control_room = pd.DataFrame(
        [
            {
                "overall_dq_score": overall_score,
                "total_records": len(market_data),
                "open_exceptions": len(exceptions),
                "high_severity_exceptions": int((exceptions["severity"] == "HIGH").sum()) if not exceptions.empty else 0,
            }
        ]
    )

    exceptions_queue = exceptions.copy()

    security_investigation = (
        exceptions.groupby(["security_id", "symbol"], as_index=False)
        .size()
        .rename(columns={"size": "exception_count"})
        if not exceptions.empty
        else pd.DataFrame(columns=["security_id", "symbol", "exception_count"])
    )

    source_reliability = (
        exceptions.groupby("source", as_index=False)
        .size()
        .rename(columns={"size": "exception_count"})
        if not exceptions.empty
        else pd.DataFrame(columns=["source", "exception_count"])
    )

    paths = {
        "control_room": output_dir / "control_room.parquet",
        "dimension_scores": output_dir / "dimension_scores.parquet",
        "exceptions_queue": output_dir / "exceptions_queue.parquet",
        "security_investigation": output_dir / "security_investigation.parquet",
        "source_reliability": output_dir / "source_reliability.parquet",
        "rule_summary": output_dir / "rule_summary.parquet",
    }

    control_room.to_parquet(paths["control_room"], index=False)
    dimension_scores.to_parquet(paths["dimension_scores"], index=False)
    exceptions_queue.to_parquet(paths["exceptions_queue"], index=False)
    security_investigation.to_parquet(paths["security_investigation"], index=False)
    source_reliability.to_parquet(paths["source_reliability"], index=False)
    rule_summary.to_parquet(paths["rule_summary"], index=False)

    return {k: str(v) for k, v in paths.items()}
