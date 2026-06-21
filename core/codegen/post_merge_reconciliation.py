from __future__ import annotations

from typing import Any, Mapping, Sequence

from core.canonical.json import canonical_hash


COMPLETION_STATUS = "ABX_CODEGEN_INTELLIGENCE_SPINE_ADVISORY_COMPUTABLE"
RECONCILIATION_SCHEMA_VERSION = "AbxCodegenPostMergeReconciliation.v1"


def build_post_merge_reconciliation_receipt(
    *,
    timestamp: str,
    completion_receipt: Mapping[str, Any],
    phase_merge_refs: Mapping[str, str],
    continuity_signals: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    path_count = completion_receipt.get("observed_path_count", 0)
    required_count = completion_receipt.get("required_path_count", 0)
    completion_hash = completion_receipt.get("canonical_hash", "NOT_COMPUTABLE")
    base: dict[str, Any] = {
        "schema_version": RECONCILIATION_SCHEMA_VERSION,
        "receipt_id": "ABX_V2.0_CODEGEN_SPINE_COMPLETION_RECEIPT",
        "receipt_status": "ABX_CODEGEN_SPINE_POST_MERGE_RECONCILED",
        "timestamp": timestamp,
        "spine_status": completion_receipt.get(
            "spine_status", "NOT_COMPUTABLE"
        ),
        "path_coverage": f"{path_count}/{required_count}",
        "completion_canonical_hash": completion_hash,
        "phase_merge_refs": dict(phase_merge_refs),
        "continuity_signals": [dict(signal) for signal in continuity_signals],
        "authority_locks": {
            "advisory_only": True,
            "canon_mutation": False,
            "runtime_mutation": False,
            "execution_authority": False,
            "github_writeback": False,
            "notion_writeback": False,
            "file_writeback": False,
            "production_activation": False,
        },
        "valid_for_execution": False,
        "valid_for_runtime_activation": False,
        "valid_for_canon_promotion": False,
        "brier_score": 0.1,
        "recommended_next": [
            "PHASE_7_SHADOW_RUNTIME_ACTIVATION_PREP",
            "PHASE_8_GLOBAL_INGEST_WIRING_STUB",
            "PHASE_9_NOTION_PROJECTION_DRYRUN",
            "PHASE_10_PLUS_OPERATOR_SELECTOR",
        ],
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_continuity_signal(
    *,
    path: str,
    status: str,
    detail: str,
    brier_score: float = 0.1,
) -> dict[str, Any]:
    return {
        "path": path,
        "status": status,
        "detail": detail,
        "brier_score": brier_score,
        "valid_for_execution": False,
    }
