from __future__ import annotations

from pathlib import Path

from core.abx_metric_dashboard import (
    ALLOWED_SYSTEM_STATES,
    build_abx_metric_dashboard_frame,
    build_abx_metric_prediction_frame,
)


def test_prediction_frame_is_deterministic_and_annotation_only() -> None:
    first = build_abx_metric_prediction_frame()
    second = build_abx_metric_prediction_frame()

    assert first == second
    assert first["packet_type"] == "ABXMetricPredictionFrame.v1"
    assert first["authority"] == "FORECAST_ANNOTATION_ONLY"
    assert first["output_effect"] == "ANNOTATION_ONLY"
    assert first["non_filtering_compliance"] is True
    assert first["forecast_batch"] == "AFE-BATCH-004.3"
    assert len(first["provenance_hash"]) == 64


def test_dashboard_frame_missing_batches_fail_closed_to_not_computable() -> None:
    frame = build_abx_metric_dashboard_frame()

    assert frame["packet_type"] == "ABXMetricDashboardFrame.v1"
    assert frame["authority"] == "SHADOW_ONLY_TRACE"
    assert frame["output_effect"] == "VISUAL_ANNOTATION_ONLY"
    assert frame["system_state"] == "NOT_COMPUTABLE"
    assert frame["localized_counterfield"] == "NOT_COMPUTABLE"
    assert "MISSING_SOURCE_BATCH:AFE-BATCH-004.1" in frame["not_computable_reasons"]
    assert frame["core_metrics"]["SDR"] == "NOT_COMPUTABLE"
    assert frame["dynamic_metrics"]["HCI"] == "NOT_COMPUTABLE"


def test_dashboard_frame_computes_when_all_sources_are_observed(tmp_path: Path) -> None:
    source_paths = {
        "AFE-BATCH-004": Path("batch004.json"),
        "AFE-BATCH-004.1": Path("batch004_1.json"),
        "AFE-BATCH-004.2": Path("batch004_2.json"),
    }
    for rel_path in source_paths.values():
        (tmp_path / rel_path).write_text("{}", encoding="utf-8")

    frame = build_abx_metric_dashboard_frame(root=tmp_path, source_batch_paths=source_paths)

    assert frame["system_state"] == "HYBRID_COLLISION"
    assert frame["localized_counterfield"] == "RECOVERY"
    assert frame["not_computable_reasons"] == []
    assert frame["core_metrics"]["MSI"] == 0.74
    assert frame["dynamic_metrics"]["HCI"] == 0.84
    assert frame["prediction_frame"]["master_forecast"] != "NOT_COMPUTABLE"


def test_dashboard_frame_preserves_non_filtering_and_authority_locks() -> None:
    frame = build_abx_metric_dashboard_frame()

    assert frame["non_filtering_compliance"] is True
    assert frame["compliance"] == {
        "output_preserved": True,
        "annotation_only": True,
        "filter_calls_detected": False,
        "suppression_calls_detected": False,
        "rewrite_calls_detected": False,
        "panel_hiding_detected": False,
    }
    assert frame["runtime_locks"]["execution_authority"] is False
    assert frame["runtime_locks"]["runtime_mutation_allowed"] is False
    assert frame["runtime_locks"]["canon_mutation_allowed"] is False
    assert frame["runtime_locks"]["forecast_weight_allowed"] is False
    assert frame["runtime_locks"]["metric_threshold_may_hide_panel"] is False
    assert frame["runtime_locks"]["candidate_metrics_require_stabilization_window"] is True


def test_system_state_enum_and_source_run_provenance() -> None:
    frame = build_abx_metric_dashboard_frame()

    assert set(frame["allowed_system_states"]) == set(ALLOWED_SYSTEM_STATES)
    assert frame["system_state"] in ALLOWED_SYSTEM_STATES
    assert frame["prediction_frame"]["system_state"] in ALLOWED_SYSTEM_STATES
    assert frame["source_run_ids"] == ["AFE-BATCH-004", "AFE-BATCH-004.1", "AFE-BATCH-004.2"]
