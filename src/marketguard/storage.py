from __future__ import annotations

import json
from pathlib import Path

import duckdb
import pandas as pd


class RawStorage:
    """Immutable raw snapshot writer for source payloads."""

    def __init__(self, raw_root: str | Path) -> None:
        self.raw_root = Path(raw_root)

    def write_market_data(self, source: str, run_id: str, df: pd.DataFrame) -> Path:
        target_dir = self.raw_root / source / "market_data"
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / f"run_{run_id}.parquet"
        df.to_parquet(target_path, index=False)
        return target_path

    def write_actions_data(self, source: str, run_id: str, df: pd.DataFrame) -> Path:
        target_dir = self.raw_root / source / "corporate_actions"
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / f"run_{run_id}.parquet"
        df.to_parquet(target_path, index=False)
        return target_path


class CanonicalStore:
    """Canonical parquet + DuckDB upsert persistence layer."""

    def __init__(self, market_data_path: str | Path, actions_data_path: str | Path, duckdb_path: str | Path) -> None:
        self.market_data_path = Path(market_data_path)
        self.actions_data_path = Path(actions_data_path)
        self.duckdb_path = Path(duckdb_path)
        self.market_data_path.parent.mkdir(parents=True, exist_ok=True)
        self.actions_data_path.parent.mkdir(parents=True, exist_ok=True)
        self.duckdb_path.parent.mkdir(parents=True, exist_ok=True)

    def upsert_market_data(self, incoming: pd.DataFrame) -> pd.DataFrame:
        if incoming.empty:
            return incoming

        if self.market_data_path.exists():
            existing = pd.read_parquet(self.market_data_path)
            merged = pd.concat([existing, incoming], ignore_index=True)
        else:
            merged = incoming.copy()

        key_cols = ["security_id", "observation_date", "source"]
        merged = merged.sort_values(key_cols + ["ingestion_timestamp"]).drop_duplicates(
            subset=key_cols,
            keep="last",
        )

        merged = merged.sort_values(["security_id", "observation_date", "source"]).reset_index(drop=True)
        merged.to_parquet(self.market_data_path, index=False)

        self._refresh_duckdb_table("canonical_market_data", self.market_data_path)

        return merged

    def upsert_actions_data(self, incoming: pd.DataFrame) -> pd.DataFrame:
        if incoming.empty:
            if self.actions_data_path.exists():
                return pd.read_parquet(self.actions_data_path)
            return incoming

        if self.actions_data_path.exists():
            existing = pd.read_parquet(self.actions_data_path)
            merged = pd.concat([existing, incoming], ignore_index=True)
        else:
            merged = incoming.copy()

        key_cols = ["security_id", "observation_date", "source", "dividend", "stock_split"]
        merged = merged.sort_values(["security_id", "observation_date", "source", "ingestion_timestamp"]).drop_duplicates(
            subset=key_cols,
            keep="last",
        )

        merged = merged.sort_values(["security_id", "observation_date", "source"]).reset_index(drop=True)
        merged.to_parquet(self.actions_data_path, index=False)

        self._refresh_duckdb_table("canonical_corporate_actions", self.actions_data_path)

        return merged

    def _refresh_duckdb_table(self, table_name: str, parquet_path: Path) -> None:
        conn = duckdb.connect(str(self.duckdb_path))
        try:
            conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM read_parquet('{parquet_path}')")
        finally:
            conn.close()


class RunMetadataStore:
    """Persist run summary metadata for reproducibility and auditability."""

    def __init__(self, metadata_dir: str | Path) -> None:
        self.metadata_dir = Path(metadata_dir)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)

    def write(self, run_id: str, payload: dict) -> Path:
        target = self.metadata_dir / f"run_{run_id}.json"
        with target.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, default=str)
        return target
