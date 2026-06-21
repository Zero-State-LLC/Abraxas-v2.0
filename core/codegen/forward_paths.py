from __future__ import annotations

from typing import Any, Mapping, Sequence

from core.canonical.json import canonical_hash


FORWARD_PATHS_SCHEMA_VERSION = "AbxCodegenForwardPathsSelector.v1"


DEFAULT_FORWARD_PATHS: tuple[dict[str, Any], ...] = (
    {
        "lane": "v2_1_roadmap_planning",
        "description": "Plan the next advisory roadmap after Codegen Spine closure.",
        "operator_selectable": True,
        "brier_score": 0.1,
    },
    {
        "lane": "hollersports_schema_generation",
        "description": "Prepare schema-generation prompts for HollerSports only.",
        "operator_selectable": True,
        "brier_score": 0.12,
    },
    {
        "lane": "runtime_unlock_prep",
        "description": "Plan runtime unlock prerequisites without activation.",
        "operator_selectable": True,
        "brier_score": 0.11,
    },
    {
        "lane": "aal_viz_cross_pollination_stub",
        "description": "Map AAL/Viz surface reuse as static docs-only stubs.",
        "operator_selectable": True,
        "brier_score": 0.12,
    },
)


def build_forward_paths_receipt(
    *,
    timestamp: str,
    source_phase_receipts: Sequence[str],
    provenance: Mapping[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": FORWARD_PATHS_SCHEMA_VERSION,
        "receipt_id": "ABX_CODEGEN_PHASE_10_PLUS_FORWARD_PATHS_SELECTOR",
        "receipt_status": "FORWARD_PATHS_SELECTOR_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "source_phase_receipts": list(source_phase_receipts),
        "operator_selectable_lanes": [dict(path) for path in DEFAULT_FORWARD_PATHS],
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
        "provenance": dict(provenance),
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}
