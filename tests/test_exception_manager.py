from pathlib import Path

import pandas as pd

from marketguard.exception_manager import initialize_exception_ledger, update_exception_status


def test_exception_lifecycle_update(tmp_path: Path) -> None:
    ledger_path = tmp_path / "exception_ledger.parquet"
    exceptions = pd.DataFrame(
        [
            {
                "exception_id": "R01_US0001_2026-01-01_yahoo_finance",
                "rule_id": "R01",
                "severity": "HIGH",
                "status": "OPEN",
                "owner": "UNASSIGNED",
                "created_at": "2026-01-01T00:00:00Z",
            }
        ]
    )

    ledger = initialize_exception_ledger(exceptions, ledger_path)
    assert len(ledger) == 1

    updated = update_exception_status(
        ledger_path=ledger_path,
        exception_id="R01_US0001_2026-01-01_yahoo_finance",
        new_status="INVESTIGATING",
        owner="analyst_1",
    )

    row = updated.iloc[0]
    assert row["status"] == "INVESTIGATING"
    assert row["owner"] == "analyst_1"
