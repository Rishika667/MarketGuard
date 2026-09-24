from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


CANONICAL_REQUIRED_COLUMNS = [
    "security_id",
    "symbol",
    "observation_date",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "source",
]

KEY_COLUMNS = ["security_id", "observation_date", "source"]


@dataclass
class ValidationResult:
    valid_data: pd.DataFrame
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)



def validate_canonical_market_data(df: pd.DataFrame) -> ValidationResult:
    """Perform Stage-1 pre-QC structural validation."""
    errors: list[str] = []
    warnings: list[str] = []

    missing_columns = [c for c in CANONICAL_REQUIRED_COLUMNS if c not in df.columns]
    if missing_columns:
        errors.append(f"Missing required columns: {missing_columns}")
        return ValidationResult(valid_data=pd.DataFrame(), errors=errors, warnings=warnings)

    data = df.copy()
    data["observation_date"] = pd.to_datetime(data["observation_date"], errors="coerce").dt.date

    invalid_dates = data["observation_date"].isna().sum()
    if invalid_dates > 0:
        warnings.append(f"Dropped {invalid_dates} rows with invalid observation_date")
        data = data[data["observation_date"].notna()].copy()

    for col in ["open", "high", "low", "close", "adjusted_close", "volume"]:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")

    null_price_rows = data[["open", "high", "low", "close"]].isna().any(axis=1)
    if null_price_rows.any():
        dropped = int(null_price_rows.sum())
        warnings.append(f"Dropped {dropped} rows with null OHLC fields")
        data = data[~null_price_rows].copy()

    ohlc_invalid = (data["high"] < data[["open", "close", "low"]].max(axis=1)) | (
        data["low"] > data[["open", "close", "high"]].min(axis=1)
    )
    if ohlc_invalid.any():
        dropped = int(ohlc_invalid.sum())
        warnings.append(f"Dropped {dropped} rows failing OHLC structural sanity")
        data = data[~ohlc_invalid].copy()

    non_positive = (data[["open", "high", "low", "close"]] <= 0).any(axis=1)
    if non_positive.any():
        dropped = int(non_positive.sum())
        warnings.append(f"Dropped {dropped} rows with non-positive prices")
        data = data[~non_positive].copy()

    duplicate_mask = data.duplicated(subset=KEY_COLUMNS, keep="last")
    if duplicate_mask.any():
        dropped = int(duplicate_mask.sum())
        warnings.append(f"Dropped {dropped} duplicate rows on key {KEY_COLUMNS}")
        data = data[~duplicate_mask].copy()

    data = data.sort_values(KEY_COLUMNS).reset_index(drop=True)

    if data.empty:
        errors.append("No valid market data rows remained after validation")

    return ValidationResult(valid_data=data, errors=errors, warnings=warnings)
