from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

import numpy as np
import pandas as pd

from marketguard.qc_engine import run_quality_controls


@dataclass
class SyntheticValidationResult:
    injected_issues: pd.DataFrame
    detection_metrics: pd.DataFrame
    detected_exceptions: pd.DataFrame


def inject_synthetic_errors(base_data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Inject controlled defects used to validate rule detectability."""
    df = base_data.copy().sort_values(["security_id", "observation_date"]).reset_index(drop=True)
    for col in ["open", "high", "low", "close", "adjusted_close", "volume"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype(float)

    injections: list[dict] = []

    if len(df) < 30:
        return df, pd.DataFrame(columns=["rule_id", "security_id", "observation_date", "source"])

    # R02 non-positive
    idx = df.index[5]
    df.loc[idx, "close"] = -1
    injections.append({"rule_id": "R02", "security_id": df.loc[idx, "security_id"], "observation_date": df.loc[idx, "observation_date"], "source": df.loc[idx, "source"]})

    # R01 bad OHLC
    idx = df.index[10]
    df.loc[idx, "high"] = df.loc[idx, "low"] - 1
    injections.append({"rule_id": "R01", "security_id": df.loc[idx, "security_id"], "observation_date": df.loc[idx, "observation_date"], "source": df.loc[idx, "source"]})

    # R04 price spike
    idx = df.index[15]
    df.loc[idx, "close"] = df.loc[idx, "close"] * 2.2
    injections.append({"rule_id": "R04", "security_id": df.loc[idx, "security_id"], "observation_date": df.loc[idx, "observation_date"], "source": df.loc[idx, "source"]})

    # R06 stale sequence
    sec = df.loc[df.index[20], "security_id"]
    src = df.loc[df.index[20], "source"]
    sec_idxs = df[(df["security_id"] == sec) & (df["source"] == src)].index[:4]
    if len(sec_idxs) >= 4:
        stale_close = df.loc[sec_idxs[0], "close"]
        df.loc[sec_idxs, "close"] = stale_close
        for ix in sec_idxs[2:]:
            injections.append({"rule_id": "R06", "security_id": df.loc[ix, "security_id"], "observation_date": df.loc[ix, "observation_date"], "source": df.loc[ix, "source"]})

    # R09 volume anomaly
    idx = df.index[25]
    df.loc[idx, "volume"] = df["volume"].median() * 50
    injections.append({"rule_id": "R09", "security_id": df.loc[idx, "security_id"], "observation_date": df.loc[idx, "observation_date"], "source": df.loc[idx, "source"]})

    # R12 adjusted inconsistency
    idx = df.index[30]
    df.loc[idx, "adjusted_close"] = df.loc[idx, "close"] * 0.5
    injections.append({"rule_id": "R12", "security_id": df.loc[idx, "security_id"], "observation_date": df.loc[idx, "observation_date"], "source": df.loc[idx, "source"]})

    injected_df = pd.DataFrame(injections).drop_duplicates().reset_index(drop=True)
    return df, injected_df


def run_synthetic_validation(
    canonical_market_data: pd.DataFrame,
    corporate_actions: pd.DataFrame,
    run_id: str,
) -> SyntheticValidationResult:
    """Run synthetic defect injection and quantify QC detection effectiveness."""
    injected_data, injected_issues = inject_synthetic_errors(canonical_market_data)

    quality_result = run_quality_controls(
        market_data=injected_data,
        corporate_actions=corporate_actions,
        run_id=f"{run_id}_synthetic",
    )
    detected = quality_result.exceptions.copy()

    if injected_issues.empty:
        metrics = pd.DataFrame(columns=["rule_id", "injected_count", "detected_count", "detection_rate", "false_positive_rate", "scored_at"])
        return SyntheticValidationResult(injected_issues=injected_issues, detection_metrics=metrics, detected_exceptions=detected)

    injected_issues["key"] = injected_issues.apply(
        lambda x: f"{x['rule_id']}|{x['security_id']}|{x['observation_date']}|{x['source']}", axis=1
    )

    detected["key"] = detected.apply(
        lambda x: f"{x['rule_id']}|{x['security_id']}|{x['observation_date']}|{x['source']}", axis=1
    )

    metrics_rows = []
    all_detected_keys = set(detected["key"].tolist())
    for rule_id, grp in injected_issues.groupby("rule_id"):
        injected_keys = set(grp["key"].tolist())
        tp = len(injected_keys & all_detected_keys)
        injected_count = len(injected_keys)

        detected_for_rule = detected[detected["rule_id"] == rule_id]
        fp = max(0, len(detected_for_rule) - tp)
        denom_fp = max(len(detected_for_rule), 1)

        metrics_rows.append(
            {
                "rule_id": rule_id,
                "injected_count": injected_count,
                "detected_count": tp,
                "detection_rate": tp / injected_count if injected_count else 0.0,
                "false_positive_rate": fp / denom_fp,
                "scored_at": datetime.now(UTC),
            }
        )

    metrics = pd.DataFrame(metrics_rows).sort_values("rule_id").reset_index(drop=True)

    return SyntheticValidationResult(injected_issues=injected_issues, detection_metrics=metrics, detected_exceptions=detected)
