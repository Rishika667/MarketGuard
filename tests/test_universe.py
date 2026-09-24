from pathlib import Path

from marketguard.universe import load_universe


def test_load_universe() -> None:
    universe = load_universe(Path("configs/security_universe.csv"))
    assert len(universe) == 150
    assert set(universe["country"].unique()) == {"US", "IN"}
    assert universe["security_id"].is_unique
