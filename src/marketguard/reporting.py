from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pandas as pd


def generate_quality_report(
    output_path: str | Path,
    overall_score: float,
    dimension_scores: pd.DataFrame,
    exceptions: pd.DataFrame,
    rule_summary: pd.DataFrame,
    synthetic_metrics: pd.DataFrame | None,
    run_context: dict,
) -> Path:
    """Generate markdown quality report from live computed outputs."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    severity_counts = (
        exceptions.groupby("severity").size().to_dict() if not exceptions.empty and "severity" in exceptions.columns else {}
    )

    lines = [
        "# MarketGuard Automated Quality Report",
        "",
        f"Generated at (UTC): {datetime.now(UTC).isoformat()}",
        f"Quality Run ID: {run_context.get('quality_run_id', 'unknown')}",
        f"Pipeline Run ID: {run_context.get('pipeline_run_id', 'unknown')}",
        "",
        "## Overview",
        f"- Overall DQ Score: **{overall_score:.2f}**",
        f"- Total Canonical Records Evaluated: {run_context.get('total_records', 0)}",
        f"- Total Exceptions: {len(exceptions)}",
        "",
        "## Dimension Scores",
    ]

    if dimension_scores.empty:
        lines.append("No dimension scores available.")
    else:
        for _, row in dimension_scores.iterrows():
            lines.append(
                f"- {row['dq_dimension']}: {row['dimension_score']:.2f} "
                f"(violations={int(row['violations'])}, rate={row['violation_rate']:.6f})"
            )

    lines.extend(["", "## Exception Severity Distribution"])
    if severity_counts:
        for sev in ["HIGH", "MEDIUM", "LOW"]:
            lines.append(f"- {sev}: {int(severity_counts.get(sev, 0))}")
    else:
        lines.append("No exceptions generated.")

    lines.extend(["", "## Rule Activity"])
    if rule_summary.empty:
        lines.append("No rule activity available.")
    else:
        active_rules = rule_summary[rule_summary["exception_count"] > 0]
        if active_rules.empty:
            lines.append("No active rule failures.")
        else:
            for _, row in active_rules.sort_values("exception_count", ascending=False).iterrows():
                lines.append(f"- {row['rule_id']} ({row['rule_name']}): {int(row['exception_count'])}")

    if synthetic_metrics is not None and not synthetic_metrics.empty:
        lines.extend(["", "## Synthetic Validation"])
        for _, row in synthetic_metrics.iterrows():
            lines.append(
                f"- {row['rule_id']}: detection_rate={row['detection_rate']:.2f}, "
                f"false_positive_rate={row['false_positive_rate']:.2f}, "
                f"detected={int(row['detected_count'])}/{int(row['injected_count'])}"
            )

    lines.extend(["", "## Source Reliability Note", "Use these outputs as observed source reliability signals, not proof of absolute data correctness."])

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path
