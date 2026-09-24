from __future__ import annotations

import argparse
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from marketguard.config import load_pipeline_config
from marketguard.dashboard_prep import build_dashboard_datasets
from marketguard.exception_manager import initialize_exception_ledger
from marketguard.logging_utils import get_logger
from marketguard.pipeline.eod_ingestion import run_pipeline
from marketguard.qc_engine import DEFAULT_QC_PARAMS, run_quality_controls
from marketguard.reporting import generate_quality_report
from marketguard.scoring_engine import build_rule_summary, calculate_dq_scores
from marketguard.synthetic_validation import run_synthetic_validation


def _quality_run_id() -> str:
    return datetime.now(UTC).strftime("Q%Y%m%dT%H%M%SZ")


def run_marketguard(config_path: str | Path, run_ingestion: bool = False, run_synthetic: bool = True) -> dict:
    """Execute full MarketGuard workflow: ingestion(optional) -> QC -> exceptions -> scoring -> outputs."""
    config = load_pipeline_config(config_path)
    logger = get_logger(config.log_dir)

    ingestion_result = None
    if run_ingestion:
        ingestion_result = run_pipeline(config_path)

    market_path = Path(config.canonical_data_path)
    actions_path = Path(config.actions_data_path)

    if not market_path.exists():
        raise FileNotFoundError(f"Canonical market dataset not found: {market_path}")

    market_data = pd.read_parquet(market_path)
    corporate_actions = pd.read_parquet(actions_path) if actions_path.exists() else pd.DataFrame()

    quality_run_id = _quality_run_id()

    quality_result = run_quality_controls(
        market_data=market_data,
        corporate_actions=corporate_actions,
        run_id=quality_run_id,
        qc_params=DEFAULT_QC_PARAMS,
    )

    scores = calculate_dq_scores(market_data=market_data, exceptions=quality_result.exceptions)
    rule_summary = build_rule_summary(quality_result.exceptions)

    synthetic_result = None
    if run_synthetic:
        synthetic_result = run_synthetic_validation(
            canonical_market_data=market_data,
            corporate_actions=corporate_actions,
            run_id=quality_run_id,
        )

    quality_dir = Path("data/processed/quality")
    quality_dir.mkdir(parents=True, exist_ok=True)

    exceptions_path = quality_dir / "exceptions.parquet"
    metrics_path = quality_dir / "qc_metrics.parquet"
    rule_summary_path = quality_dir / "rule_summary.parquet"
    dimension_scores_path = quality_dir / "dimension_scores.parquet"
    overall_score_path = quality_dir / "overall_score.parquet"
    synthetic_metrics_path = quality_dir / "synthetic_validation_metrics.parquet"
    exception_ledger_path = quality_dir / "exception_ledger.parquet"

    quality_result.exceptions.to_parquet(exceptions_path, index=False)
    quality_result.metrics.to_parquet(metrics_path, index=False)
    rule_summary.to_parquet(rule_summary_path, index=False)
    scores.dimension_scores.to_parquet(dimension_scores_path, index=False)
    pd.DataFrame([{"quality_run_id": quality_run_id, "overall_dq_score": scores.overall_score}]).to_parquet(
        overall_score_path, index=False
    )

    if synthetic_result is not None:
        synthetic_result.detection_metrics.to_parquet(synthetic_metrics_path, index=False)

    exception_ledger = initialize_exception_ledger(quality_result.exceptions, exception_ledger_path)

    report_path = generate_quality_report(
        output_path=Path("reports/generated") / f"quality_report_{quality_run_id}.md",
        overall_score=scores.overall_score,
        dimension_scores=scores.dimension_scores,
        exceptions=quality_result.exceptions,
        rule_summary=rule_summary,
        synthetic_metrics=synthetic_result.detection_metrics if synthetic_result is not None else None,
        run_context={
            "quality_run_id": quality_run_id,
            "pipeline_run_id": ingestion_result["run_id"] if ingestion_result else "existing_canonical_dataset",
            "total_records": len(market_data),
        },
    )

    dashboard_paths = build_dashboard_datasets(
        output_dir=Path("data/processed/dashboard"),
        market_data=market_data,
        exceptions=quality_result.exceptions,
        dimension_scores=scores.dimension_scores,
        overall_score=scores.overall_score,
        rule_summary=rule_summary,
    )

    result = {
        "quality_run_id": quality_run_id,
        "overall_dq_score": scores.overall_score,
        "exception_count": int(len(quality_result.exceptions)),
        "paths": {
            "exceptions": str(exceptions_path),
            "qc_metrics": str(metrics_path),
            "rule_summary": str(rule_summary_path),
            "dimension_scores": str(dimension_scores_path),
            "overall_score": str(overall_score_path),
            "synthetic_metrics": str(synthetic_metrics_path) if synthetic_result is not None else "",
            "exception_ledger": str(exception_ledger_path),
            "report": str(report_path),
            "dashboard": dashboard_paths,
        },
        "exception_ledger_rows": int(len(exception_ledger)),
        "ingestion": ingestion_result,
    }

    logger.info("Completed MarketGuard full workflow", extra={"context": result})
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run full MarketGuard pipeline")
    parser.add_argument("--config", default="configs/pipeline.yaml")
    parser.add_argument("--run-ingestion", action="store_true", help="Run live ingestion before quality workflow")
    parser.add_argument("--skip-synthetic-validation", action="store_true", help="Skip synthetic validation phase")
    args = parser.parse_args()

    run_marketguard(
        config_path=args.config,
        run_ingestion=args.run_ingestion,
        run_synthetic=not args.skip_synthetic_validation,
    )


if __name__ == "__main__":
    main()
