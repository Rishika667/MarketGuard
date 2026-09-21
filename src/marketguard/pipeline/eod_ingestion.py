from __future__ import annotations

import argparse
import hashlib
from datetime import UTC, date, datetime
from pathlib import Path

import pandas as pd

from marketguard.adapters.factory import build_adapter
from marketguard.config import load_pipeline_config
from marketguard.logging_utils import get_logger
from marketguard.normalization import normalize_corporate_actions, normalize_market_data
from marketguard.storage import CanonicalStore, RawStorage, RunMetadataStore
from marketguard.universe import load_universe
from marketguard.validation import validate_canonical_market_data


def _resolve_date_window(history_years: int, end_date: str | date | None) -> tuple[date, date]:
    if isinstance(end_date, date):
        end = end_date
    elif isinstance(end_date, str):
        end = date.fromisoformat(end_date)
    else:
        end = datetime.now(UTC).date()

    start = date(end.year - history_years, end.month, end.day)
    return start, end


def _build_run_id(source_name: str, start_date: date, end_date: date) -> str:
    now = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    digest = hashlib.sha1(f"{source_name}|{start_date}|{end_date}|{now}".encode("utf-8")).hexdigest()[:8]
    return f"{now}_{digest}"


def run_pipeline(config_path: str | Path) -> dict:
    config = load_pipeline_config(config_path)
    logger = get_logger(config.log_dir)

    adapter = build_adapter(config.source_name, request_sleep_seconds=config.request_sleep_seconds)
    universe = load_universe(config.universe_file)
    start_date, end_date = _resolve_date_window(config.history_years, config.end_date)
    run_id = _build_run_id(config.source_name, start_date, end_date)

    logger.info(
        "Starting Stage-1 ingestion run",
        extra={
            "context": {
                "run_id": run_id,
                "source": config.source_name,
                "universe_size": len(universe),
                "start_date": str(start_date),
                "end_date": str(end_date),
            }
        },
    )

    raw_market_frames: list[pd.DataFrame] = []
    raw_action_frames: list[pd.DataFrame] = []
    canonical_market_frames: list[pd.DataFrame] = []
    canonical_action_frames: list[pd.DataFrame] = []

    failures: list[dict] = []

    for _, security in universe.iterrows():
        symbol = str(security["yahoo_symbol"])
        try:
            payload = adapter.fetch_security_data(symbol=symbol, start_date=start_date, end_date=end_date)
        except Exception as exc:  # noqa: BLE001
            failures.append(
                {
                    "security_id": security["security_id"],
                    "symbol": security["symbol"],
                    "reason": "source_failure",
                    "detail": str(exc),
                }
            )
            logger.error(
                "Source fetch failed",
                extra={
                    "context": {
                        "run_id": run_id,
                        "security_id": security["security_id"],
                        "symbol": security["symbol"],
                        "source_symbol": symbol,
                        "error": str(exc),
                    }
                },
            )
            continue

        retrieved_at = datetime.now(UTC)

        market_raw = payload.market_data.copy()
        market_raw["security_id"] = security["security_id"]
        market_raw["symbol"] = security["symbol"]
        market_raw["source_symbol"] = symbol
        market_raw["source"] = config.source_name
        market_raw["run_id"] = run_id
        market_raw["retrieved_at"] = retrieved_at

        actions_raw = payload.corporate_actions.copy()
        actions_raw["security_id"] = security["security_id"]
        actions_raw["symbol"] = security["symbol"]
        actions_raw["source_symbol"] = symbol
        actions_raw["source"] = config.source_name
        actions_raw["run_id"] = run_id
        actions_raw["retrieved_at"] = retrieved_at

        raw_market_frames.append(market_raw)
        if not actions_raw.empty:
            raw_action_frames.append(actions_raw)

        normalized_market = normalize_market_data(market_raw, security, config.source_name, run_id)
        validation = validate_canonical_market_data(normalized_market)

        for warning in validation.warnings:
            logger.warning(
                "Validation warning",
                extra={
                    "context": {
                        "run_id": run_id,
                        "security_id": security["security_id"],
                        "symbol": security["symbol"],
                        "warning": warning,
                    }
                },
            )

        if validation.errors:
            failures.append(
                {
                    "security_id": security["security_id"],
                    "symbol": security["symbol"],
                    "reason": "validation_failure",
                    "detail": "; ".join(validation.errors),
                }
            )
            logger.error(
                "Validation failed",
                extra={
                    "context": {
                        "run_id": run_id,
                        "security_id": security["security_id"],
                        "symbol": security["symbol"],
                        "errors": validation.errors,
                    }
                },
            )
            continue

        canonical_market_frames.append(validation.valid_data)

        normalized_actions = normalize_corporate_actions(actions_raw, security, config.source_name, run_id)
        if not normalized_actions.empty:
            canonical_action_frames.append(normalized_actions)

    raw_storage = RawStorage(config.raw_data_dir)
    canonical_store = CanonicalStore(config.canonical_data_path, config.actions_data_path, config.duckdb_path)
    metadata_store = RunMetadataStore(config.run_metadata_dir)

    raw_market_data = pd.concat(raw_market_frames, ignore_index=True) if raw_market_frames else pd.DataFrame()
    raw_actions_data = pd.concat(raw_action_frames, ignore_index=True) if raw_action_frames else pd.DataFrame()
    canonical_market_data = pd.concat(canonical_market_frames, ignore_index=True) if canonical_market_frames else pd.DataFrame()
    canonical_actions_data = pd.concat(canonical_action_frames, ignore_index=True) if canonical_action_frames else pd.DataFrame()

    raw_market_path = raw_storage.write_market_data(config.source_name, run_id, raw_market_data)
    raw_actions_path = raw_storage.write_actions_data(config.source_name, run_id, raw_actions_data)

    canonical_after_upsert = canonical_store.upsert_market_data(canonical_market_data)
    actions_after_upsert = canonical_store.upsert_actions_data(canonical_actions_data)

    status = "success"
    if failures and len(failures) < len(universe):
        status = "partial_success"
    elif failures and len(failures) == len(universe):
        status = "failed"

    result = {
        "run_id": run_id,
        "status": status,
        "source": config.source_name,
        "window": {"start_date": str(start_date), "end_date": str(end_date)},
        "universe_size": int(len(universe)),
        "raw_market_rows": int(len(raw_market_data)),
        "raw_action_rows": int(len(raw_actions_data)),
        "canonical_rows_written_this_run": int(len(canonical_market_data)),
        "canonical_total_rows": int(len(canonical_after_upsert)),
        "corporate_actions_total_rows": int(len(actions_after_upsert)),
        "failure_count": int(len(failures)),
        "failures": failures,
        "output_paths": {
            "raw_market_data": str(raw_market_path),
            "raw_actions_data": str(raw_actions_path),
            "canonical_market_data": str(config.canonical_data_path),
            "canonical_actions_data": str(config.actions_data_path),
            "duckdb": str(config.duckdb_path),
        },
    }

    metadata_path = metadata_store.write(run_id, result)
    result["output_paths"]["run_metadata"] = str(metadata_path)

    logger.info("Completed Stage-1 ingestion run", extra={"context": result})

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="MarketGuard Stage-1 EOD ingestion pipeline")
    parser.add_argument(
        "--config",
        default="configs/pipeline.yaml",
        help="Path to pipeline configuration YAML",
    )
    args = parser.parse_args()

    run_pipeline(args.config)


if __name__ == "__main__":
    main()
