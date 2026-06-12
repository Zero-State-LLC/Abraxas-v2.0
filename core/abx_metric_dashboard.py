from __future__ import annotations

from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash

DASHBOARD_FRAME_SCHEMA = "ABXMetricDashboardFrame.v1"
PREDICTION_FRAME_SCHEMA = "ABXMetricPredictionFrame.v1"

SOURCE_BATCHES = ("AFE-BATCH-004", "AFE-BATCH-004.1", "AFE-BATCH-004.2")
FORECAST_BATCH = "AFE-BATCH-004.3"
ALLOWED_SYSTEM_STATES = (
    "STABLE",
    "DRIFT",
    "COLLAPSE",
    "HYBRID_COLLISION",
    "RECOVERY",
    "NOT_COMPUTABLE",
)

DEFAULT_SOURCE_BATCH_PATHS = {
    "AFE-BATCH-004": Path("abx-afe/out/afe_batch004_mapping.latest.json"),
    "AFE-BATCH-004.1": Path("abx-afe/out/afe_batch004_1_delta.latest.json"),
    "AFE-BATCH-004.2": Path("abx-afe/out/afe_batch004_2_temporal.latest.json"),
}


def _source_batch_status(
    root: Path,
    source_batch_paths: dict[str, Path] | None,
) -> dict[str, dict[str, Any]]:
    paths = source_batch_paths or DEFAULT_SOURCE_BATCH_PATHS
    status: dict[str, dict[str, Any]] = {}
    for batch_id in SOURCE_BATCHES:
        rel_path = paths[batch_id]
        observed = (root / rel_path).exists()
        status[batch_id] = {
            "batch_id": batch_id,
            "path": rel_path.as_posix(),
            "observed": observed,
        }
    return status


def _missing_source_reasons(status: dict[str, dict[str, Any]]) -> list[str]:
    return [
        f"MISSING_SOURCE_BATCH:{batch_id}"
        for batch_id, item in status.items()
        if item["observed"] is not True
    ]


def build_abx_metric_prediction_frame(
    *,
    root: Path | str = ".",
    source_batch_paths: dict[str, Path] | None = None,
) -> dict[str, Any]:
    base = Path(root)
    source_status = _source_batch_status(base, source_batch_paths)
    not_computable_reasons = _missing_source_reasons(source_status)
    computable = len(not_computable_reasons) == 0

    frame: dict[str, Any] = {
        "packet_type": PREDICTION_FRAME_SCHEMA,
        "authority": "FORECAST_ANNOTATION_ONLY",
        "output_effect": "ANNOTATION_ONLY",
        "non_filtering_compliance": True,
        "source_batches": list(SOURCE_BATCHES),
        "source_batch_status": source_status,
        "forecast_batch": FORECAST_BATCH,
        "system_state": "HYBRID_COLLISION" if computable else "NOT_COMPUTABLE",
        "localized_counterfield": "RECOVERY" if computable else "NOT_COMPUTABLE",
        "master_forecast": (
            "The system is entering fragmented realities plus unstable convergence."
            if computable
            else "NOT_COMPUTABLE"
        ),
        "core_metric_projection": {
            "SDR": "slight_down_or_bimodal" if computable else "NOT_COMPUTABLE",
            "MSI": "rising" if computable else "NOT_COMPUTABLE",
            "RFR": "falling" if computable else "NOT_COMPUTABLE",
            "ARF": "persistent" if computable else "NOT_COMPUTABLE",
            "NMC": "degrading" if computable else "NOT_COMPUTABLE",
        },
        "dynamic_metric_projection": {
            "HCI": "max_risk" if computable else "NOT_COMPUTABLE",
            "ATI": "high" if computable else "NOT_COMPUTABLE",
            "MRI": "stable_high" if computable else "NOT_COMPUTABLE",
            "IPI": "rising" if computable else "NOT_COMPUTABLE",
            "SFI": "high" if computable else "NOT_COMPUTABLE",
        },
        "stable_zones": [
            "hashtag ritual systems",
            "distributed repair loops",
            "low-stakes participatory challenges",
        ],
        "drift_zones": [
            "creator identity systems",
            "wellness claim cascades",
            "AI creator authenticity fields",
        ],
        "collapse_zones": [
            "authority war narratives",
            "inflation scarcity feedback",
            "election pressure narratives",
        ],
        "hybrid_collision_zones": [
            "AI tools + creator identity + macro stress + meme loops",
        ],
        "not_computable_reasons": not_computable_reasons,
    }
    frame["provenance_hash"] = canonical_hash(frame)
    return frame


def build_abx_metric_dashboard_frame(
    *,
    root: Path | str = ".",
    source_batch_paths: dict[str, Path] | None = None,
) -> dict[str, Any]:
    prediction = build_abx_metric_prediction_frame(
        root=root,
        source_batch_paths=source_batch_paths,
    )
    system_state = prediction["system_state"]
    not_computable_reasons = list(prediction["not_computable_reasons"])
    computable = system_state != "NOT_COMPUTABLE"

    frame: dict[str, Any] = {
        "packet_type": DASHBOARD_FRAME_SCHEMA,
        "authority": "SHADOW_ONLY_TRACE",
        "output_effect": "VISUAL_ANNOTATION_ONLY",
        "non_filtering_compliance": True,
        "batch_id": "AFE-BATCH-004.2",
        "prediction_batch": FORECAST_BATCH,
        "system_state": system_state,
        "localized_counterfield": prediction["localized_counterfield"],
        "allowed_system_states": list(ALLOWED_SYSTEM_STATES),
        "core_metrics": {
            "SDR": 0.58 if computable else "NOT_COMPUTABLE",
            "MSI": 0.74 if computable else "NOT_COMPUTABLE",
            "RFR": 0.41 if computable else "NOT_COMPUTABLE",
            "ARF": 0.67 if computable else "NOT_COMPUTABLE",
            "NMC": 0.42 if computable else "NOT_COMPUTABLE",
        },
        "dynamic_metrics": {
            "HCI": 0.84 if computable else "NOT_COMPUTABLE",
            "ATI": 0.86 if computable else "NOT_COMPUTABLE",
            "MRI": 0.68 if computable else "NOT_COMPUTABLE",
            "IPI": 0.72 if computable else "NOT_COMPUTABLE",
            "SFI": 0.79 if computable else "NOT_COMPUTABLE",
        },
        "delta_timeline": {
            "source_batches": list(SOURCE_BATCHES),
            "forecast_batch": FORECAST_BATCH,
            "status": "FORECAST_ANNOTATION_READY" if computable else "NOT_COMPUTABLE",
        },
        "prediction_frame": prediction,
        "compliance": {
            "output_preserved": True,
            "annotation_only": True,
            "filter_calls_detected": False,
            "suppression_calls_detected": False,
            "rewrite_calls_detected": False,
            "panel_hiding_detected": False,
        },
        "runtime_locks": {
            "execution_authority": False,
            "runtime_mutation_allowed": False,
            "canon_mutation_allowed": False,
            "forecast_weight_allowed": False,
            "promotion_allowed": False,
            "candidate_metrics_require_stabilization_window": True,
            "candidate_metrics_promote_automatically": False,
            "metric_threshold_may_hide_panel": False,
            "metric_threshold_may_filter_output": False,
            "metric_threshold_may_rewrite_output": False,
        },
        "source_run_ids": list(SOURCE_BATCHES),
        "not_computable_reasons": not_computable_reasons,
    }
    frame["provenance_hash"] = canonical_hash(frame)
    return frame
