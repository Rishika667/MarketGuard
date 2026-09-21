from __future__ import annotations

from datetime import UTC, datetime

import pandas as pd


def normalize_market_data(
    raw_df: pd.DataFrame,
    security_row: pd.Series,
    source: str,
    run_id: str,
) -> pd.DataFrame:
    """Normalize source market data to canonical MarketGuard schema."""
    if raw_df.empty:
        return pd.DataFrame(
            columns=[
                "security_id",
                "symbol",
                "country",
                "market",
                "exchange",
                "currency",
                "observation_date",
                "open",
                "high",
                "low",
                "close",
                "adjusted_close",
                "volume",
                "source",
                "ingestion_timestamp",
                "run_id",
                "data_status",
            ]
        )

    mapping = {
        "Date": "observation_date",
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Adj Close": "adjusted_close",
        "Volume": "volume",
    }

    normalized = raw_df.rename(columns=mapping).copy()

    normalized["security_id"] = security_row["security_id"]
    normalized["symbol"] = security_row["symbol"]
    normalized["country"] = security_row["country"]
    normalized["market"] = security_row["market"]
    normalized["exchange"] = security_row["exchange"]
    normalized["currency"] = security_row["currency"]
    normalized["source"] = source
    normalized["run_id"] = run_id
    normalized["ingestion_timestamp"] = datetime.now(UTC)

    normalized["observation_date"] = pd.to_datetime(normalized["observation_date"], errors="coerce").dt.date

    for col in ["open", "high", "low", "close", "adjusted_close", "volume"]:
        if col in normalized.columns:
            normalized[col] = pd.to_numeric(normalized[col], errors="coerce")

    normalized["data_status"] = "ok"
    if "adjusted_close" in normalized.columns:
        normalized.loc[normalized["adjusted_close"].isna(), "data_status"] = "missing_adjusted_close"

    canonical_columns = [
        "security_id",
        "symbol",
        "country",
        "market",
        "exchange",
        "currency",
        "observation_date",
        "open",
        "high",
        "low",
        "close",
        "adjusted_close",
        "volume",
        "source",
        "ingestion_timestamp",
        "run_id",
        "data_status",
    ]

    for col in canonical_columns:
        if col not in normalized.columns:
            normalized[col] = pd.NA

    normalized = normalized[canonical_columns]

    return normalized.sort_values(["security_id", "observation_date"]).reset_index(drop=True)


def normalize_corporate_actions(
    actions_df: pd.DataFrame,
    security_row: pd.Series,
    source: str,
    run_id: str,
) -> pd.DataFrame:
    """Normalize corporate-action payload into canonical actions schema."""
    if actions_df.empty:
        return pd.DataFrame(
            columns=[
                "security_id",
                "symbol",
                "observation_date",
                "dividend",
                "stock_split",
                "country",
                "market",
                "exchange",
                "currency",
                "source",
                "ingestion_timestamp",
                "run_id",
            ]
        )

    mapping = {
        "Date": "observation_date",
        "Dividends": "dividend",
        "Stock Splits": "stock_split",
    }

    normalized = actions_df.rename(columns=mapping).copy()

    if "observation_date" not in normalized.columns:
        normalized["observation_date"] = pd.NaT
    normalized["observation_date"] = pd.to_datetime(normalized["observation_date"], errors="coerce").dt.date

    if "dividend" not in normalized.columns:
        normalized["dividend"] = 0.0
    if "stock_split" not in normalized.columns:
        normalized["stock_split"] = 0.0

    normalized["dividend"] = pd.to_numeric(normalized["dividend"], errors="coerce").fillna(0.0)
    normalized["stock_split"] = pd.to_numeric(normalized["stock_split"], errors="coerce").fillna(0.0)

    normalized["security_id"] = security_row["security_id"]
    normalized["symbol"] = security_row["symbol"]
    normalized["country"] = security_row["country"]
    normalized["market"] = security_row["market"]
    normalized["exchange"] = security_row["exchange"]
    normalized["currency"] = security_row["currency"]
    normalized["source"] = source
    normalized["run_id"] = run_id
    normalized["ingestion_timestamp"] = datetime.now(UTC)

    canonical_columns = [
        "security_id",
        "symbol",
        "observation_date",
        "dividend",
        "stock_split",
        "country",
        "market",
        "exchange",
        "currency",
        "source",
        "ingestion_timestamp",
        "run_id",
    ]

    for col in canonical_columns:
        if col not in normalized.columns:
            normalized[col] = pd.NA

    normalized = normalized[canonical_columns]
    normalized = normalized[(normalized["dividend"] != 0.0) | (normalized["stock_split"] != 0.0)]

    return normalized.sort_values(["security_id", "observation_date"]).reset_index(drop=True)
