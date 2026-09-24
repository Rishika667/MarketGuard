from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class PipelineConfig:
    source_name: str
    universe_file: Path
    raw_data_dir: Path
    canonical_data_path: Path
    actions_data_path: Path
    duckdb_path: Path
    run_metadata_dir: Path
    log_dir: Path
    history_years: int
    end_date: str | date | None
    request_sleep_seconds: float


class ConfigError(ValueError):
    """Raised when pipeline configuration is invalid."""


def _require(config: dict[str, Any], key: str) -> Any:
    if key not in config:
        raise ConfigError(f"Missing required config key: {key}")
    return config[key]


def load_pipeline_config(config_path: str | Path) -> PipelineConfig:
    """Load Stage-1 pipeline configuration from YAML."""
    config_path = Path(config_path)
    with config_path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    if not isinstance(raw, dict):
        raise ConfigError("Pipeline config must be a mapping")

    paths = _require(raw, "paths")
    source = _require(raw, "source")
    runtime = _require(raw, "runtime")

    if not isinstance(paths, dict) or not isinstance(source, dict) or not isinstance(runtime, dict):
        raise ConfigError("Config sections paths/source/runtime must be mappings")

    end_date = runtime.get("end_date")
    if isinstance(end_date, date):
        end_date = end_date.isoformat()

    return PipelineConfig(
        source_name=str(_require(source, "name")),
        universe_file=Path(_require(paths, "universe_file")),
        raw_data_dir=Path(_require(paths, "raw_data_dir")),
        canonical_data_path=Path(_require(paths, "canonical_data_path")),
        actions_data_path=Path(_require(paths, "actions_data_path")),
        duckdb_path=Path(_require(paths, "duckdb_path")),
        run_metadata_dir=Path(_require(paths, "run_metadata_dir")),
        log_dir=Path(_require(paths, "log_dir")),
        history_years=int(_require(runtime, "history_years")),
        end_date=end_date,
        request_sleep_seconds=float(runtime.get("request_sleep_seconds", 0.0)),
    )
