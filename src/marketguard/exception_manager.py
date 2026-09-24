from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

VALID_STATUSES = {"OPEN", "INVESTIGATING", "RESOLVED", "OVERRIDDEN"}


def initialize_exception_ledger(exceptions: pd.DataFrame, ledger_path: str | Path) -> pd.DataFrame:
    """Initialize/update persistent exception ledger with lifecycle fields."""
    ledger_path = Path(ledger_path)
    ledger_path.parent.mkdir(parents=True, exist_ok=True)

    base = exceptions.copy()
    if base.empty:
        empty = pd.DataFrame(columns=[
            "exception_id",
            "rule_id",
            "severity",
            "status",
            "owner",
            "created_at",
            "updated_at",
            "resolution_note",
        ])
        empty.to_parquet(ledger_path, index=False)
        return empty

    base["status"] = base.get("status", "OPEN").fillna("OPEN")
    base["owner"] = base.get("owner", "UNASSIGNED").fillna("UNASSIGNED")
    base["updated_at"] = datetime.now(UTC)
    base["resolution_note"] = base.get("resolution_note", pd.Series([None] * len(base)))

    if ledger_path.exists():
        existing = pd.read_parquet(ledger_path)
        merged = pd.concat([existing, base], ignore_index=True)
        merged = merged.sort_values(["exception_id", "updated_at"]).drop_duplicates(subset=["exception_id"], keep="last")
    else:
        merged = base

    merged.to_parquet(ledger_path, index=False)
    return merged


def update_exception_status(
    ledger_path: str | Path,
    exception_id: str,
    new_status: str,
    owner: str | None = None,
    resolution_note: str | None = None,
) -> pd.DataFrame:
    """Update lifecycle status of a specific exception."""
    if new_status not in VALID_STATUSES:
        raise ValueError(f"Invalid status {new_status}. Must be one of {sorted(VALID_STATUSES)}")

    ledger_path = Path(ledger_path)
    if not ledger_path.exists():
        raise FileNotFoundError(f"Exception ledger not found: {ledger_path}")

    ledger = pd.read_parquet(ledger_path)
    mask = ledger["exception_id"] == exception_id
    if not mask.any():
        raise KeyError(f"Exception not found: {exception_id}")

    ledger.loc[mask, "status"] = new_status
    ledger.loc[mask, "updated_at"] = datetime.now(UTC)

    if owner is not None:
        ledger.loc[mask, "owner"] = owner
    if resolution_note is not None:
        ledger.loc[mask, "resolution_note"] = resolution_note

    ledger.to_parquet(ledger_path, index=False)
    return ledger
