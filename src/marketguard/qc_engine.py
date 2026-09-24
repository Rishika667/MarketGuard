from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import numpy as np
import pandas as pd


RULE_CATALOG: dict[str, dict[str, str]] = {
    "R01": {"name": "Invalid OHLC relationship", "dimension": "validity", "issue_type": "invalid_ohlc"},
    "R02": {"name": "Non-positive price", "dimension": "validity", "issue_type": "non_positive_price"},
    "R03": {"name": "Missing required observation", "dimension": "completeness", "issue_type": "missing_observation"},
    "R04": {"name": "Extreme return anomaly", "dimension": "validity", "issue_type": "extreme_return"},
    "R05": {"name": "Potential corporate-action anomaly", "dimension": "consistency", "issue_type": "potential_corporate_action"},
    "R06": {"name": "Stale price sequence", "dimension": "timeliness", "issue_type": "stale_price"},
    "R07": {"name": "Cross-source price break", "dimension": "cross_source_consistency", "issue_type": "cross_source_break"},
    "R08": {"name": "Missing trading day gap", "dimension": "completeness", "issue_type": "missing_trading_day"},
    "R09": {"name": "Volume anomaly", "dimension": "consistency", "issue_type": "volume_anomaly"},
    "R10": {"name": "Freshness breach", "dimension": "timeliness", "issue_type": "freshness_breach"},
    "R11": {"name": "Duplicate observation", "dimension": "consistency", "issue_type": "duplicate_observation"},
    "R12": {"name": "Adjusted/unadjusted inconsistency", "dimension": "consistency", "issue_type": "adjusted_unadjusted_inconsistency"},
}


DEFAULT_QC_PARAMS: dict[str, Any] = {
    "r04_abs_return_threshold": 0.2,
    "r04_vol_multiplier": 5.0,
    "r05_split_signature_threshold": 0.35,
    "r06_stale_days": 3,
    "r07_cross_source_diff_pct": 0.03,
    "r08_business_day_gap": 3,
    "r09_volume_zscore": 4.0,
    "r10_freshness_lag_days": 3,
    "r12_adjusted_close_diff_pct": 0.1,
}


@dataclass
class QCRunResult:
    exceptions: pd.DataFrame
    metrics: pd.DataFrame


def _severity_from_magnitude(rule_id: str, magnitude: float | int | None) -> str:
    if magnitude is None or (isinstance(magnitude, float) and np.isnan(magnitude)):
        return "MEDIUM"

    value = abs(float(magnitude))
    if rule_id in {"R01", "R02", "R11"}:
        return "HIGH"
    if value >= 0.5:
        return "HIGH"
    if value >= 0.2:
        return "MEDIUM"
    return "LOW"


def _build_exception_rows(
    df: pd.DataFrame,
    rule_id: str,
    magnitude_col: str | None,
    evidence_cols: list[str],
    run_id: str,
) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    rows = df.copy()
    catalog = RULE_CATALOG[rule_id]

    rows["rule_id"] = rule_id
    rows["rule_name"] = catalog["name"]
    rows["dq_dimension"] = catalog["dimension"]
    rows["issue_type"] = catalog["issue_type"]
    rows["status"] = "OPEN"
    rows["owner"] = "UNASSIGNED"
    rows["quality_run_id"] = run_id
    rows["created_at"] = datetime.now(UTC)

    def _evidence_payload(record: pd.Series) -> str:
        payload = {k: record.get(k) for k in evidence_cols if k in record.index}
        return json.dumps(payload, default=str)

    rows["evidence"] = rows.apply(_evidence_payload, axis=1)

    if magnitude_col and magnitude_col in rows.columns:
        rows["magnitude"] = rows[magnitude_col]
    else:
        rows["magnitude"] = np.nan

    rows["severity"] = rows["magnitude"].apply(lambda x: _severity_from_magnitude(rule_id, x))

    rows["exception_id"] = rows.apply(
        lambda x: f"{rule_id}_{x['security_id']}_{x['observation_date']}_{x.get('source', 'na')}", axis=1
    )

    keep_cols = [
        "exception_id",
        "quality_run_id",
        "rule_id",
        "rule_name",
        "issue_type",
        "dq_dimension",
        "severity",
        "status",
        "owner",
        "security_id",
        "symbol",
        "country",
        "market",
        "exchange",
        "currency",
        "observation_date",
        "source",
        "evidence",
        "created_at",
    ]

    for col in keep_cols:
        if col not in rows.columns:
            rows[col] = pd.NA

    return rows[keep_cols]


def run_quality_controls(
    market_data: pd.DataFrame,
    corporate_actions: pd.DataFrame | None,
    run_id: str,
    qc_params: dict[str, Any] | None = None,
) -> QCRunResult:
    """Execute MarketGuard QC rules R01-R12 and generate exceptions."""
    if market_data.empty:
        return QCRunResult(exceptions=pd.DataFrame(), metrics=pd.DataFrame())

    params = {**DEFAULT_QC_PARAMS, **(qc_params or {})}
    df = market_data.copy()
    df["observation_date"] = pd.to_datetime(df["observation_date"]).dt.date
    df["ingestion_timestamp"] = pd.to_datetime(df["ingestion_timestamp"], errors="coerce")

    for col in ["open", "high", "low", "close", "adjusted_close", "volume"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.sort_values(["security_id", "observation_date", "source"]).reset_index(drop=True)

    actions = corporate_actions.copy() if corporate_actions is not None and not corporate_actions.empty else pd.DataFrame()
    if not actions.empty:
        actions["observation_date"] = pd.to_datetime(actions["observation_date"], errors="coerce").dt.date

    exceptions_frames: list[pd.DataFrame] = []

    # R01 Invalid OHLC relationship
    r01 = df[(df["high"] < df[["open", "close", "low"]].max(axis=1)) | (df["low"] > df[["open", "close", "high"]].min(axis=1))]
    exceptions_frames.append(_build_exception_rows(r01, "R01", None, ["open", "high", "low", "close"], run_id))

    # R02 Non-positive price
    r02_mask = (df[["open", "high", "low", "close"]] <= 0).any(axis=1)
    r02 = df[r02_mask].copy()
    r02["magnitude"] = df[["open", "high", "low", "close"]].min(axis=1)
    exceptions_frames.append(_build_exception_rows(r02, "R02", "magnitude", ["open", "high", "low", "close"], run_id))

    # R03 Missing required observation against market-level calendar
    r03_rows: list[dict[str, Any]] = []
    for market, mkt_df in df.groupby("market"):
        market_dates = sorted(set(mkt_df["observation_date"].dropna()))
        if not market_dates:
            continue
        market_date_set = set(market_dates)
        columns_for_context = ["security_id", "symbol", "country", "market", "exchange", "currency", "source"]
        base_context = mkt_df[columns_for_context].drop_duplicates(subset=["security_id", "source"])
        for _, ctx in base_context.iterrows():
            sec_dates = set(
                mkt_df[(mkt_df["security_id"] == ctx["security_id"]) & (mkt_df["source"] == ctx["source"])][
                    "observation_date"
                ].dropna()
            )
            missing_dates = sorted(market_date_set - sec_dates)
            for missing_date in missing_dates:
                r03_rows.append({**ctx.to_dict(), "observation_date": missing_date, "missing_count": 1})

    r03 = pd.DataFrame(r03_rows)
    exceptions_frames.append(_build_exception_rows(r03, "R03", "missing_count", ["missing_count"], run_id))

    # Compute returns for several rules
    df["prev_close"] = df.groupby(["security_id", "source"])["close"].shift(1)
    df["daily_return"] = (df["close"] / df["prev_close"]) - 1.0

    # R04 Extreme return / volatility outlier
    df["rolling_vol"] = (
        df.groupby(["security_id", "source"])["daily_return"].rolling(20, min_periods=10).std().reset_index(level=[0, 1], drop=True)
    )
    r04 = df[
        df["daily_return"].abs()
        > np.maximum(params["r04_abs_return_threshold"], params["r04_vol_multiplier"] * df["rolling_vol"].fillna(0.0))
    ].copy()
    r04["magnitude"] = r04["daily_return"].abs()
    exceptions_frames.append(_build_exception_rows(r04, "R04", "magnitude", ["daily_return", "rolling_vol"], run_id))

    # R05 Potential corporate-action anomaly
    r05 = df[df["daily_return"].abs() >= params["r05_split_signature_threshold"]].copy()
    if not actions.empty:
        action_flags = actions[["security_id", "observation_date", "source", "stock_split", "dividend"]].copy()
        action_flags["has_action"] = (action_flags["stock_split"].fillna(0) != 0) | (action_flags["dividend"].fillna(0) != 0)
        r05 = r05.merge(
            action_flags[["security_id", "observation_date", "source", "has_action"]],
            on=["security_id", "observation_date", "source"],
            how="left",
        )
        r05["has_action"] = r05["has_action"].astype("boolean").fillna(False)
        r05 = r05[~r05["has_action"]].copy()
    r05["magnitude"] = r05["daily_return"].abs()
    exceptions_frames.append(_build_exception_rows(r05, "R05", "magnitude", ["daily_return"], run_id))

    # R06 Stale price sequence
    stale_days = int(params["r06_stale_days"])
    stale_records: list[pd.DataFrame] = []
    for (_, _), group in df.groupby(["security_id", "source"]):
        grp = group.copy().sort_values("observation_date")
        grp["is_same_close"] = grp["close"].eq(grp["close"].shift(1))
        grp["streak"] = grp["is_same_close"].groupby((~grp["is_same_close"]).cumsum()).cumsum()
        stale_records.append(grp[grp["streak"] >= stale_days])
    r06 = pd.concat(stale_records, ignore_index=True) if stale_records else pd.DataFrame()
    if not r06.empty:
        r06["magnitude"] = r06["streak"]
    exceptions_frames.append(_build_exception_rows(r06, "R06", "magnitude", ["close", "streak"], run_id))

    # R07 Cross-source price break
    source_count = df["source"].nunique()
    if source_count >= 2:
        pivot = (
            df.pivot_table(index=["security_id", "observation_date"], columns="source", values="close", aggfunc="mean")
            .reset_index()
            .dropna(axis=0, how="any")
        )
        close_cols = [c for c in pivot.columns if c not in {"security_id", "observation_date"}]
        if len(close_cols) >= 2:
            pivot["min_close"] = pivot[close_cols].min(axis=1)
            pivot["max_close"] = pivot[close_cols].max(axis=1)
            pivot["pct_diff"] = (pivot["max_close"] - pivot["min_close"]) / pivot["min_close"].replace(0, np.nan)
            flagged = pivot[pivot["pct_diff"] > params["r07_cross_source_diff_pct"]]
            r07 = flagged.merge(
                df[["security_id", "symbol", "country", "market", "exchange", "currency", "observation_date"]].drop_duplicates(
                    subset=["security_id", "observation_date"]
                ),
                on=["security_id", "observation_date"],
                how="left",
            )
            r07["source"] = "MULTI_SOURCE"
            r07["magnitude"] = r07["pct_diff"]
        else:
            r07 = pd.DataFrame()
    else:
        r07 = pd.DataFrame()
    exceptions_frames.append(_build_exception_rows(r07, "R07", "magnitude", ["pct_diff", "min_close", "max_close"], run_id))

    # R08 Missing trading day gap
    gap_records: list[pd.DataFrame] = []
    max_gap = int(params["r08_business_day_gap"])
    for (_, _), group in df.groupby(["security_id", "source"]):
        grp = group.copy().sort_values("observation_date")
        grp["date"] = pd.to_datetime(grp["observation_date"])
        grp["prev_date"] = grp["date"].shift(1)
        grp["business_gap"] = grp.apply(
            lambda x: np.busday_count(x["prev_date"].date(), x["date"].date()) if pd.notna(x["prev_date"]) else 0,
            axis=1,
        )
        gap_records.append(grp[grp["business_gap"] > max_gap])
    r08 = pd.concat(gap_records, ignore_index=True) if gap_records else pd.DataFrame()
    if not r08.empty:
        r08["magnitude"] = r08["business_gap"]
    exceptions_frames.append(_build_exception_rows(r08, "R08", "magnitude", ["business_gap", "prev_date"], run_id))

    # R09 Volume anomaly
    r09 = df.copy()
    r09["rolling_vol_mean"] = r09.groupby(["security_id", "source"])["volume"].rolling(20, min_periods=10).mean().reset_index(
        level=[0, 1], drop=True
    )
    r09["rolling_vol_std"] = r09.groupby(["security_id", "source"])["volume"].rolling(20, min_periods=10).std().reset_index(
        level=[0, 1], drop=True
    )
    r09["volume_z"] = (r09["volume"] - r09["rolling_vol_mean"]) / r09["rolling_vol_std"].replace(0, np.nan)
    r09 = r09[r09["volume_z"].abs() > params["r09_volume_zscore"]].copy()
    r09["magnitude"] = r09["volume_z"].abs()
    exceptions_frames.append(_build_exception_rows(r09, "R09", "magnitude", ["volume", "volume_z"], run_id))

    # R10 Freshness breach
    latest_global_date = df["observation_date"].max()
    freshness = (
        df.groupby(["security_id", "symbol", "country", "market", "exchange", "currency", "source"], as_index=False)[
            "observation_date"
        ]
        .max()
        .rename(columns={"observation_date": "latest_observation_date"})
    )
    freshness["observation_date"] = freshness["latest_observation_date"]
    freshness["lag_days"] = freshness["latest_observation_date"].apply(
        lambda d: np.busday_count(d, latest_global_date) if pd.notna(d) and pd.notna(latest_global_date) else np.nan
    )
    r10 = freshness[freshness["lag_days"] > params["r10_freshness_lag_days"]].copy()
    r10["magnitude"] = r10["lag_days"]
    exceptions_frames.append(_build_exception_rows(r10, "R10", "magnitude", ["latest_observation_date", "lag_days"], run_id))

    # R11 Duplicate observation
    dup_mask = df.duplicated(subset=["security_id", "observation_date", "source"], keep=False)
    r11 = df[dup_mask].copy()
    r11["magnitude"] = (
        r11.groupby(["security_id", "observation_date", "source"])["security_id"].transform("count")
    )
    exceptions_frames.append(_build_exception_rows(r11, "R11", "magnitude", ["close", "volume"], run_id))

    # R12 Adjusted/unadjusted inconsistency
    r12 = df[df["close"].notna() & df["adjusted_close"].notna()].copy()
    r12["adj_close_pct_diff"] = (r12["adjusted_close"] - r12["close"]).abs() / r12["close"].replace(0, np.nan)
    r12 = r12[r12["adj_close_pct_diff"] > params["r12_adjusted_close_diff_pct"]]
    if not actions.empty:
        action_days = actions[(actions["stock_split"].fillna(0) != 0) | (actions["dividend"].fillna(0) != 0)][
            ["security_id", "observation_date", "source"]
        ].drop_duplicates()
        r12 = r12.merge(action_days.assign(has_action=True), on=["security_id", "observation_date", "source"], how="left")
        r12["has_action"] = r12["has_action"].astype("boolean").fillna(False)
        r12 = r12[~r12["has_action"]]
    r12["magnitude"] = r12["adj_close_pct_diff"]
    exceptions_frames.append(_build_exception_rows(r12, "R12", "magnitude", ["close", "adjusted_close", "adj_close_pct_diff"], run_id))

    exceptions = pd.concat([f for f in exceptions_frames if not f.empty], ignore_index=True) if exceptions_frames else pd.DataFrame()
    if not exceptions.empty:
        exceptions = exceptions.drop_duplicates(subset=["exception_id"], keep="last")
        exceptions = exceptions.sort_values(["rule_id", "security_id", "observation_date"]).reset_index(drop=True)

    metrics = (
        exceptions.groupby(["rule_id", "severity"], as_index=False)
        .size()
        .rename(columns={"size": "exception_count"})
        if not exceptions.empty
        else pd.DataFrame(columns=["rule_id", "severity", "exception_count"])
    )

    return QCRunResult(exceptions=exceptions, metrics=metrics)
