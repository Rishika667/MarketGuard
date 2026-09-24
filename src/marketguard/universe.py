from __future__ import annotations

from pathlib import Path

import pandas as pd

REQUIRED_UNIVERSE_COLUMNS = [
    "security_id",
    "symbol",
    "yahoo_symbol",
    "market",
    "exchange",
    "country",
    "currency",
    "is_active",
]


class UniverseError(ValueError):
    """Raised when universe file has invalid structure."""


def load_universe(universe_file: str | Path, active_only: bool = True) -> pd.DataFrame:
    """Load configured security universe for ingestion."""
    universe = pd.read_csv(universe_file)

    missing = [col for col in REQUIRED_UNIVERSE_COLUMNS if col not in universe.columns]
    if missing:
        raise UniverseError(f"Universe file missing required columns: {missing}")

    if active_only:
        universe = universe[universe["is_active"].astype(bool)]

    if universe["security_id"].duplicated().any():
        raise UniverseError("Universe contains duplicate security_id values")

    if universe[["symbol", "yahoo_symbol"]].isna().any().any():
        raise UniverseError("Universe contains missing symbols")

    return universe.sort_values(["country", "symbol"]).reset_index(drop=True)
