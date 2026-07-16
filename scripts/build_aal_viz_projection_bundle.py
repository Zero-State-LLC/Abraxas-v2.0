#!/usr/bin/env python3
"""
AAL-Viz Artifact Index Adapter — read-only projection bundle builder.

Reads:  out/metric_operator/ and out/projections/wasserstein_* artifact files.
        out/chamfer_*/  artifact files.
Writes: apps/aal-viz-live-console/public/projection-bundle.json
        out/projections/aal_viz_yggdrasil_topology_v1.latest.json
        out/projections/aal_viz_yggdrasil_topology_integrity_v1.latest.json
Embeds: out/projections/aal_viz_yggdrasil_topology_delta_intelligence_v1.latest.json
        when it is valid and current-generation bound.
        out/projections/aal_viz_route_receipt_advisory_alerts_v1.latest.json
        when it is valid and bound to the embedded delta generation.

Authority constraints (always enforced):
  projection_only              = true
  runtime_mutation_allowed     = false
  promotion_allowed            = false
  production_activation_allowed = false

Never reads:  research_canary artifacts.
Fails closed: on missing or malformed source artifacts (writes FAIL_CLOSED bundle).
"""
from __future__ import annotations

import json
import hashlib
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.live_projection_health_migration_artifact import (  # noqa: E402
    build_combined_health_migration_artifact_posture,
)
from core.aal_viz_temporal_diff import generation_id  # noqa: E402
from core.aal_viz_yggdrasil_topology import (  # noqa: E402
    SOURCE_KEYS as YGGDRASIL_TOPOLOGY_SOURCE_KEYS,
    bind_yggdrasil_topology,
    build_yggdrasil_topology,
    operator_topology_payload,
    validate_yggdrasil_topology,
)
from core.aal_viz_yggdrasil_topology_integrity import (  # noqa: E402
    evaluate_yggdrasil_topology_integrity,
    validate_yggdrasil_topology_integrity,
)
from core.aal_viz_yggdrasil_topology_delta_intelligence import (  # noqa: E402
    validate_yggdrasil_topology_delta_intelligence,
)
from core.aal_viz_route_receipt_advisory_alerts import (  # noqa: E402
    validate_route_receipt_advisory_alerts,
)

OUTPUT_PATH = ROOT / "apps" / "aal-viz-live-console" / "public" / "projection-bundle.json"
YGGDRASIL_TOPOLOGY_OUTPUT_PATH = (
    ROOT / "out" / "projections" / "aal_viz_yggdrasil_topology_v1.latest.json"
)
YGGDRASIL_TOPOLOGY_INTEGRITY_OUTPUT_PATH = (
    ROOT
    / "out"
    / "projections"
    / "aal_viz_yggdrasil_topology_integrity_v1.latest.json"
)
YGGDRASIL_TOPOLOGY_DELTA_INTELLIGENCE_OUTPUT_PATH = (
    ROOT
    / "out"
    / "projections"
    / "aal_viz_yggdrasil_topology_delta_intelligence_v1.latest.json"
)
ROUTE_RECEIPT_ADVISORY_ALERTS_OUTPUT_PATH = (
    ROOT
    / "out"
    / "projections"
    / "aal_viz_route_receipt_advisory_alerts_v1.latest.json"
)
OPERATOR_PLATFORM_SCHEMA_PATH = (
    ROOT / "contracts" / "canon" / "aal_viz_operator_platform_projection.v0.2.schema.json"
)
TEMPORAL_DIFF_SCHEMA_PATH = (
    ROOT / "contracts" / "canon" / "aal_viz_temporal_diff.v1.schema.json"
)
YGGDRASIL_TOPOLOGY_SCHEMA_PATH = (
    ROOT / "contracts" / "canon" / "aal_viz_yggdrasil_topology.v1.schema.json"
)
YGGDRASIL_TOPOLOGY_INTEGRITY_SCHEMA_PATH = (
    ROOT
    / "contracts"
    / "canon"
    / "aal_viz_yggdrasil_topology_integrity.v1.schema.json"
)
YGGDRASIL_TOPOLOGY_DELTA_INTELLIGENCE_SCHEMA_PATH = (
    ROOT
    / "contracts"
    / "canon"
    / "aal_viz_yggdrasil_topology_delta_intelligence.v1.schema.json"
)
ROUTE_RECEIPT_ADVISORY_ALERTS_SCHEMA_PATH = (
    ROOT
    / "contracts"
    / "canon"
    / "aal_viz_route_receipt_advisory_alerts.v1.schema.json"
)
P40_FUSION_OVERLAY_ARTIFACT = (
    "out/projections/aal_viz_climate_motif_fusion_overlay_001.latest.json"
)
OPERATOR_NARRATIVE_OVERLAY_ARTIFACT = (
    "out/projections/operator_narrative_report_ui_overlay_001.latest.json"
)
SUBSYSTEM_HEALTH_DASHBOARD_RECEIPT = (
    "out/audit/subsystem_health_dashboard_001.latest.json"
)
CONTINUITY_NAMESPACE_MIGRATION_PREFLIGHT_RECEIPT = (
    "out/audit/continuity_namespace_migration_preflight_001.latest.json"
)
SCHEMA_VERSION = "AALViz.LiveConsoleProjectionBundle.v0.2"
GENERATED_BY = "BUILD_AAL_VIZ_PROJECTION_BUNDLE_001"

OPERATOR_PLATFORM_SOURCES = {
    "operator_console": "out/audit/operator_runtime_console_001.latest.json",
    "graph_render": "out/projections/aal_viz_graph_render_packet_001.latest.json",
    "yggdrasil": "out/audit/yggdrasil_coupling_map_001.latest.json",
    "temporal_diff": "out/projections/aal_viz_temporal_diff_v1.latest.json",
    "production_slice": (
        "out/stabilization_readiness/surface_resolution_001/"
        "production_slice_candidate.latest.json"
    ),
    "surface_receipt": (
        "out/stabilization_readiness/surface_resolution_001/"
        "surface_resolution_receipt.latest.json"
    ),
    "contract_inventory": (
        "out/stabilization_readiness/contract_inventory_002/"
        "production_contract_inventory.latest.json"
    ),
    "contract_receipt": (
        "out/stabilization_readiness/contract_inventory_002/"
        "contract_inventory_receipt.latest.json"
    ),
}

AUTHORITY: dict[str, bool] = {
    "projection_only": True,
    "runtime_mutation_allowed": False,
    "promotion_allowed": False,
    "production_activation_allowed": False,
}

# ── Operator definitions ─────────────────────────────────────────────────────
# artifact_sequence: ordered chain progression (relative to ROOT)
# computation_receipt_key: key within artifact_sequence whose presence + content
#   indicates computation was executed
# promotion_key: key indicating baseline promotion complete → READY
# shadow_only_posture: non-None means chain is blocked at shadow-stub stage

OPERATOR_DEFS: dict[str, dict[str, Any]] = {
    "wasserstein": {
        "display_name": "WASSERSTEIN",
        "artifact_sequence": [
            "out/projections/wasserstein_distance_implementation_readiness_dossier_001.latest.json",
            "out/projections/wasserstein_test_vector_schema_plan_001.latest.json",
            "out/projections/wasserstein_test_vector_fixture_plan_001.latest.json",
            "out/projections/wasserstein_fixture_plan_consolidation_receipt_001.latest.json",
            "out/projections/wasserstein_test_vector_fixture_creation_authorization_review_001.latest.json",
            "out/projections/wasserstein_test_vector_fixture_creation_actual_pr_gate_001.latest.json",
            "out/projections/wasserstein_test_vector_fixture_file_creation_receipt_001.latest.json",
            "out/projections/wasserstein_test_vector_fixture_schema_validation_complete_review_001.latest.json",
            "out/projections/wasserstein_expected_values_gate_001.latest.json",
            "out/projections/wasserstein_expected_values_addition_receipt_001.latest.json",
            "out/projections/wasserstein_expected_values_complete_review_001.latest.json",
            "out/projections/wasserstein_test_vector_computation_authorization_review_001.latest.json",
            "out/projections/wasserstein_test_vector_computation_receipt_001.latest.json",
            "out/projections/wasserstein_test_vector_computation_complete_review_001.latest.json",
            "out/projections/wasserstein_test_vector_computation_actual_pr_gate_001.latest.json",
            "out/metric_operator/wasserstein_cpu_baseline_implementation_plan_001.latest.json",
            "out/metric_operator/wasserstein_cpu_baseline_validation_plan_001.latest.json",
            "out/metric_operator/wasserstein_cpu_baseline_actual_pr_gate_review_001.latest.json",
            "out/metric_operator/wasserstein_cpu_baseline_computation_receipt_001.latest.json",
            "out/metric_operator/wasserstein_cpu_baseline_computation_complete_review_001.latest.json",
            "out/metric_operator/wasserstein_cpu_baseline_computation_operator_closure_001.latest.json",
            "out/metric_operator/wasserstein_cpu_baseline_pack_vector_update_001.latest.json",
            "out/metric_operator/wasserstein_baseline_promotion_review_001.latest.json",
            "out/metric_operator/wasserstein_baseline_promotion_complete_001.latest.json",
        ],
        "computation_receipt_key": (
            "out/projections/wasserstein_test_vector_computation_receipt_001.latest.json"
        ),
        "promotion_key": None,
        "shadow_only_posture": "SHADOW_STUB_ONLY",
        "cpu_baseline_phase_closed_key": (
            "out/metric_operator/wasserstein_cpu_baseline_pack_vector_update_001.latest.json"
        ),
        "baseline_promotion_complete_key": (
            "out/metric_operator/wasserstein_baseline_promotion_complete_001.latest.json"
        ),
        "baseline_promotion_complete_reason": (
            "WASSERSTEIN baseline promotion phase closed with no-op parity; "
            "authority remains advisory-only."
        ),
    },
    "chamfer_distance": {
        "display_name": "CHAMFER DISTANCE",
        "artifact_sequence": [
            "out/chamfer_baseline_implementation_plan/chamfer_baseline_implementation_plan_001.latest.json",
            "out/chamfer_test_vector_schema_plan/chamfer_test_vector_schema_plan_001.latest.json",
            "out/chamfer_fixture_plan_consolidation_receipt/chamfer_fixture_plan_consolidation_receipt_001.latest.json",
            "out/chamfer_fixture_creation_actual_pr_gate/chamfer_fixture_creation_actual_pr_gate_001.latest.json",
            "out/chamfer_expected_values_gate/chamfer_expected_values_gate_001.latest.json",
            "out/chamfer_expected_values_addition_receipt/chamfer_expected_values_addition_receipt_001.latest.json",
            "out/chamfer_expected_values_complete_review/chamfer_expected_values_complete_review_001.latest.json",
            "out/chamfer_distance_computation_authorization_review/chamfer_distance_computation_authorization_review_001.latest.json",
            "out/chamfer_distance_computation_receipt/chamfer_distance_computation_receipt_001.latest.json",
            "out/chamfer_distance_computation_complete_review/chamfer_distance_computation_complete_review_001.latest.json",
            "out/metric_operator/chamfer_baseline_promotion_review_001.latest.json",
            "out/metric_operator/chamfer_baseline_promotion_complete_001.latest.json",
        ],
        "computation_receipt_key": (
            "out/chamfer_distance_computation_receipt/chamfer_distance_computation_receipt_001.latest.json"
        ),
        "promotion_key": None,
        "shadow_only_posture": "SHADOW_STUB_ONLY",
        "baseline_promotion_complete_key": (
            "out/metric_operator/chamfer_baseline_promotion_complete_001.latest.json"
        ),
        "baseline_promotion_complete_reason": (
            "CHAMFER baseline promotion phase closed; "
            "authority remains advisory-only."
        ),
    },
    "geodesic": {
        "display_name": "GEODESIC",
        "artifact_sequence": [
            "out/metric_operator/geodesic_distance_implementation_readiness_dossier_001.latest.json",
            "out/metric_operator/geodesic_test_vector_schema_plan_001.latest.json",
            "out/metric_operator/geodesic_test_vector_fixture_plan_001.latest.json",
            "out/metric_operator/geodesic_expected_values_gate_001.latest.json",
            "out/metric_operator/geodesic_expected_values_addition_receipt_001.latest.json",
            "out/metric_operator/geodesic_expected_values_complete_review_001.latest.json",
            "out/metric_operator/geodesic_computation_implementation_gate_001.latest.json",
            "out/metric_operator/geodesic_computation_receipt_001.latest.json",
            "out/metric_operator/geodesic_computation_complete_review_001.latest.json",
            "out/metric_operator/geodesic_computation_operator_closure_001.latest.json",
            "out/metric_operator/geodesic_baseline_promotion_review_001.latest.json",
            "out/metric_operator/geodesic_baseline_promotion_complete_001.latest.json",
        ],
        "computation_receipt_key": (
            "out/metric_operator/geodesic_computation_receipt_001.latest.json"
        ),
        "promotion_key": "out/metric_operator/geodesic_baseline_promotion_complete_001.latest.json",
        "shadow_only_posture": None,
    },
    "norm_geometry": {
        "display_name": "NORM GEOMETRY",
        "artifact_sequence": [
            "out/metric_operator/norm_geometry_distance_implementation_readiness_dossier_001.latest.json",
            "out/metric_operator/norm_geometry_test_vector_schema_plan_001.latest.json",
            "out/metric_operator/norm_geometry_cpu_baseline_implementation_plan_001.latest.json",
            "out/metric_operator/norm_geometry_cpu_baseline_validation_plan_001.latest.json",
            "out/metric_operator/norm_geometry_cpu_baseline_actual_pr_gate_review_001.latest.json",
            "out/metric_operator/norm_geometry_computation_implementation_gate_001.latest.json",
            "out/metric_operator/norm_geometry_computation_receipt_001.latest.json",
            "out/metric_operator/norm_geometry_computation_complete_review_001.latest.json",
            "out/metric_operator/norm_geometry_computation_operator_closure_001.latest.json",
            "out/metric_operator/norm_geometry_baseline_promotion_gate_001.latest.json",
            "out/metric_operator/norm_geometry_baseline_promotion_review_001.latest.json",
            "out/metric_operator/norm_geometry_baseline_promotion_complete_001.latest.json",
        ],
        "computation_receipt_key": (
            "out/metric_operator/norm_geometry_computation_receipt_001.latest.json"
        ),
        "promotion_key": (
            "out/metric_operator/norm_geometry_baseline_promotion_complete_001.latest.json"
        ),
        "shadow_only_posture": None,
    },
    "transport": {
        "display_name": "TRANSPORT",
        "artifact_sequence": [
            "out/metric_operator/transport_distance_implementation_readiness_dossier_001.latest.json",
            "out/metric_operator/transport_test_vector_schema_plan_001.latest.json",
            "out/metric_operator/transport_cpu_baseline_implementation_plan_001.latest.json",
            "out/metric_operator/transport_cpu_baseline_validation_plan_001.latest.json",
            "out/metric_operator/transport_cpu_baseline_actual_pr_gate_review_001.latest.json",
            "out/metric_operator/transport_implementation_authorization_decision_record_001.latest.json",
            "out/metric_operator/transport_computation_implementation_gate_001.latest.json",
            "out/metric_operator/transport_fixture_corpus_creation_plan_001.latest.json",
            "out/metric_operator/transport_fixture_corpus_creation_receipt_001.latest.json",
            "out/metric_operator/transport_computation_receipt_001.latest.json",
            "out/metric_operator/transport_baseline_promotion_review_001.latest.json",
            "out/metric_operator/transport_baseline_promotion_complete_001.latest.json",
        ],
        "computation_receipt_key": (
            "out/metric_operator/transport_computation_receipt_001.latest.json"
        ),
        "promotion_key": None,
        "shadow_only_posture": "SHADOW_STUB_ONLY",
        "baseline_promotion_complete_key": (
            "out/metric_operator/transport_baseline_promotion_complete_001.latest.json"
        ),
        "baseline_promotion_complete_reason": (
            "TRANSPORT baseline promotion phase closed; "
            "authority remains advisory-only."
        ),
    },
    "heavy_tail": {
        "display_name": "HEAVY TAIL",
        "artifact_sequence": [
            "out/metric_operator/heavy_tail_shadow_stub_implementation_authorization_001.latest.json",
            "out/metric_operator/heavy_tail_test_vector_schema_plan_001.latest.json",
            "out/metric_operator/heavy_tail_fixture_corpus_creation_plan_001.latest.json",
            "out/metric_operator/heavy_tail_fixture_corpus_creation_receipt_001.latest.json",
            "out/metric_operator/heavy_tail_computation_receipt_001.latest.json",
            "out/metric_operator/heavy_tail_baseline_promotion_review_001.latest.json",
            "out/metric_operator/heavy_tail_baseline_promotion_complete_001.latest.json",
        ],
        "computation_receipt_key": (
            "out/metric_operator/heavy_tail_computation_receipt_001.latest.json"
        ),
        "promotion_key": None,
        "shadow_only_posture": "SHADOW_STUB_ONLY",
        "baseline_promotion_complete_key": (
            "out/metric_operator/heavy_tail_baseline_promotion_complete_001.latest.json"
        ),
        "baseline_promotion_complete_reason": (
            "HEAVY_TAIL baseline promotion phase closed; "
            "authority remains advisory-only."
        ),
    },
}

# ── Helpers ──────────────────────────────────────────────────────────────────


def _guard_no_research_canary(path: Path) -> None:
    parts = path.parts
    for part in parts:
        if part.startswith("research_canary"):
            raise ValueError(
                f"Forbidden: research_canary artifact access blocked: {path}"
            )


def _load_safe(path: Path) -> dict[str, Any] | None:
    """Return parsed JSON or None; never reads research_canary; fails closed on malform."""
    _guard_no_research_canary(path)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except PermissionError:
        return None
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"WARN malformed JSON in {path.relative_to(ROOT)}: {exc}\n")
        return None


def _utc_now() -> str:
    source_date_epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if source_date_epoch is not None:
        try:
            timestamp = int(source_date_epoch)
        except ValueError as exc:
            raise ValueError("SOURCE_DATE_EPOCH must be an integer") from exc
        return datetime.fromtimestamp(timestamp, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _short_hash(h: str | None) -> str:
    if not h:
        return "N/A"
    return h[:16] + "…"


# ── Per-operator projection builder ─────────────────────────────────────────


def _build_operator_projection(op_id: str, cfg: dict[str, Any]) -> dict[str, Any]:
    seq: list[str] = cfg["artifact_sequence"]
    total = len(seq)

    loaded: dict[str, dict[str, Any]] = {}
    for rel in seq:
        p = ROOT / rel
        data = _load_safe(p)
        if data is not None:
            loaded[rel] = data

    present_count = len(loaded)
    raw_pct = int(present_count / total * 100) if total > 0 else 0

    receipt_rel: str | None = cfg.get("computation_receipt_key")
    promotion_rel: str | None = cfg.get("promotion_key")
    shadow_posture: str | None = cfg.get("shadow_only_posture")

    receipt = loaded.get(receipt_rel) if receipt_rel else None
    promotion = loaded.get(promotion_rel) if promotion_rel else None
    cpu_baseline_closed_rel: str | None = cfg.get("cpu_baseline_phase_closed_key")
    cpu_baseline_closed = loaded.get(cpu_baseline_closed_rel) if cpu_baseline_closed_rel else None
    baseline_promo_complete_rel: str | None = cfg.get("baseline_promotion_complete_key")
    baseline_promo_complete = (
        loaded.get(baseline_promo_complete_rel) if baseline_promo_complete_rel else None
    )

    reason: str = ""

    if baseline_promo_complete is not None and shadow_posture is not None:
        status = "READY_SHADOW_STUB_CLOSED"
        risk_level = "LOW"
        completion_pct = 100
        reason = cfg.get(
            "baseline_promotion_complete_reason",
            "Baseline promotion phase closed; authority remains advisory-only.",
        )
    elif promotion is not None:
        status = "READY"
        risk_level = "LOW"
        completion_pct = 100
    elif cpu_baseline_closed is not None:
        phase_record = cpu_baseline_closed.get("cpu_baseline_phase_record", {})
        phase_status = phase_record.get("cpu_baseline_computation_phase_status", "")
        baseline_promoted = cpu_baseline_closed.get("authority_locks", {}).get(
            "baseline_promotion_authorized", True
        )
        if phase_status == "COMPUTATION_PHASE_CLOSED" and baseline_promoted is False:
            status = "PARTIAL_WITH_CPU_BASELINE_CLOSED"
            risk_level = "MEDIUM"
            completion_pct = 95
            reason = (
                "WASSERSTEIN CPU baseline computation phase closed; "
                "baseline promotion still blocked."
            )
        else:
            status = "PARTIAL"
            risk_level = "MEDIUM"
            completion_pct = min(raw_pct, 78)
    elif receipt is not None:
        # computation_executed may be at top level or nested in authority_locks
        auth_locks: dict[str, Any] = receipt.get("authority_locks", {})
        comp_executed: bool = receipt.get(
            "computation_executed",
            auth_locks.get("computation_executed", True),
        )
        if comp_executed is False or shadow_posture == "SHADOW_STUB_ONLY":
            status = "PARTIAL"
            risk_level = "MEDIUM"
            completion_pct = min(raw_pct, 78)
        else:
            status = "READY"
            risk_level = "LOW"
            completion_pct = min(raw_pct, 95)
    elif present_count > 0:
        status = "PARTIAL"
        risk_level = "MEDIUM" if raw_pct >= 40 else "HIGH"
        completion_pct = raw_pct
    else:
        status = "NOT_COMPUTABLE"
        risk_level = "HIGH"
        completion_pct = 0

    # Projection packets from terminal present artifact
    packets: list[dict[str, Any]] = []
    terminal_rel = seq[-1] if present_count == total else (
        next((r for r in reversed(seq) if r in loaded), None)
    )
    terminal = loaded.get(terminal_rel) if terminal_rel else None
    if terminal:
        packets.append(
            {
                "packet_id": f"{op_id}-pkt-chain-posture",
                "packet_type": "CHAIN_POSTURE",
                "status": status,
                "display_value": f"{present_count}/{total}_INDEXED",
                "authority_source": "ARTIFACT_INDEX_ADAPTER",
                "projection_only": True,
            }
        )
        if terminal.get("canonical_hash"):
            packets.append(
                {
                    "packet_id": f"{op_id}-pkt-terminal-seal",
                    "packet_type": "TERMINAL_SEAL",
                    "status": "RESOLVED",
                    "display_value": _short_hash(terminal["canonical_hash"]),
                    "authority_source": "ARTIFACT_INDEX_ADAPTER",
                    "projection_only": True,
                }
            )

    # Ledger receipts: one entry per indexed artifact
    ledger_receipts: list[dict[str, Any]] = []
    for rel in seq:
        art = loaded.get(rel)
        if art and art.get("canonical_hash"):
            stem = Path(rel).name.replace(".latest.json", "").upper()
            ledger_receipts.append(
                {
                    "receipt_id": f"{op_id}-{Path(rel).stem}",
                    "event": stem[:64],
                    "timestamp": art.get("created_at_utc", "UNKNOWN"),
                    "canonical_hash": art["canonical_hash"],
                }
            )

    source_artifacts = [r for r in seq if r in loaded]

    return {
        "system_id": op_id,
        "display_name": cfg["display_name"],
        "status": status,
        "completion_pct": completion_pct,
        "risk_level": risk_level,
        "reason": reason,
        "last_updated": _utc_now(),
        "shadow_only": True,
        "projection_packets": packets,
        "ledger_receipts": ledger_receipts,
        "_source_artifacts": source_artifacts,
    }


# ── Operator queue builder ───────────────────────────────────────────────────


def _build_operator_queue(
    systems: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    queue: list[dict[str, Any]] = []
    status_map = {s["system_id"]: s["status"] for s in systems}

    if status_map.get("transport") == "READY_SHADOW_STUB_CLOSED":
        queue.append(
            {
                "action_id": "oq-transport-001",
                "action_type": "REVIEW_CHAIN_STATE",
                "label": (
                    "TRANSPORT: baseline promotion phase closed — "
                    "shadow-stub posture preserved; authority advisory-only"
                ),
                "target_system": "transport",
                "status": "REVIEWED",
                "auto_apply_blocked": True,
                "requires_operator_review": False,
            }
        )
    elif status_map.get("transport") == "PARTIAL":
        queue.append(
            {
                "action_id": "oq-transport-001",
                "action_type": "REVIEW_CHAIN_STATE",
                "label": "TRANSPORT: fixture corpus sealed, computation not yet executed",
                "target_system": "transport",
                "status": "PENDING",
                "auto_apply_blocked": True,
                "requires_operator_review": True,
            }
        )
    wasserstein_status = status_map.get("wasserstein")
    if wasserstein_status == "READY_SHADOW_STUB_CLOSED":
        queue.append(
            {
                "action_id": "oq-wasserstein-001",
                "action_type": "REVIEW_CHAIN_STATE",
                "label": (
                    "WASSERSTEIN: baseline promotion phase closed — "
                    "shadow-stub posture preserved; authority advisory-only"
                ),
                "target_system": "wasserstein",
                "status": "REVIEWED",
                "auto_apply_blocked": True,
                "requires_operator_review": False,
            }
        )
    elif wasserstein_status == "PARTIAL_WITH_CPU_BASELINE_CLOSED":
        queue.append(
            {
                "action_id": "oq-wasserstein-001",
                "action_type": "REVIEW_CHAIN_STATE",
                "label": (
                    "WASSERSTEIN: CPU baseline phase closed — "
                    "WASSERSTEIN_BASELINE_PROMOTION_DECISION required"
                ),
                "target_system": "wasserstein",
                "status": "PENDING",
                "auto_apply_blocked": True,
                "requires_operator_review": True,
            }
        )
    elif wasserstein_status == "PARTIAL":
        queue.append(
            {
                "action_id": "oq-wasserstein-001",
                "action_type": "REVIEW_CHAIN_STATE",
                "label": "WASSERSTEIN: shadow-stub-only posture — baseline gate-cond-005 unmet",
                "target_system": "wasserstein",
                "status": "PENDING",
                "auto_apply_blocked": True,
                "requires_operator_review": True,
            }
        )
    if status_map.get("chamfer_distance") == "READY_SHADOW_STUB_CLOSED":
        queue.append(
            {
                "action_id": "oq-chamfer-001",
                "action_type": "REVIEW_CHAIN_STATE",
                "label": (
                    "CHAMFER DISTANCE: baseline promotion phase closed — "
                    "shadow-stub posture preserved; authority advisory-only"
                ),
                "target_system": "chamfer_distance",
                "status": "REVIEWED",
                "auto_apply_blocked": True,
                "requires_operator_review": False,
            }
        )
    elif status_map.get("chamfer_distance") == "READY":
        queue.append(
            {
                "action_id": "oq-chamfer-001",
                "action_type": "REVIEW_CHAIN_STATE",
                "label": "CHAMFER DISTANCE: computation complete, baseline promotion not yet executed",
                "target_system": "chamfer_distance",
                "status": "REVIEWED",
                "auto_apply_blocked": True,
                "requires_operator_review": True,
            }
        )

    return queue


# ── P40 fusion overlay ingest ────────────────────────────────────────────────


def _build_fusion_overlay_packet(p40: dict[str, Any]) -> dict[str, Any]:
    nodes: list[dict[str, Any]] = []
    for item in p40.get("overlay_nodes", []):
        if not isinstance(item, dict):
            continue
        node_id = str(item.get("node_id", "")).strip()
        if not node_id:
            continue
        node: dict[str, Any] = {"node_id": node_id}
        for key in ("label", "posture", "layer_id"):
            if key in item and item[key] is not None:
                node[key] = str(item[key])
        nodes.append(node)

    edges: list[dict[str, Any]] = []
    for item in p40.get("overlay_edges", []):
        if not isinstance(item, dict):
            continue
        edge_id = str(item.get("edge_id", "")).strip()
        source_node_id = str(item.get("source_node_id", "")).strip()
        target_node_id = str(item.get("target_node_id", "")).strip()
        if not edge_id or not source_node_id or not target_node_id:
            continue
        edge: dict[str, Any] = {
            "edge_id": edge_id,
            "source_node_id": source_node_id,
            "target_node_id": target_node_id,
        }
        if "relation" in item and item["relation"] is not None:
            edge["relation"] = str(item["relation"])
        edges.append(edge)

    return {
        "packet_type": "AALVizClimateMotifFusionOverlay.v1",
        "final_status": str(p40.get("final_status", "NOT_COMPUTABLE")),
        "fusion_posture": str(p40.get("fusion_posture", "NOT_COMPUTABLE")),
        "overlay_nodes": nodes,
        "overlay_edges": edges,
        "governance_flags": {
            "advisory_only": True,
            "projection_only": True,
        },
    }


def _load_fusion_overlay() -> tuple[dict[str, Any] | None, str | None]:
    p40 = _load_safe(ROOT / P40_FUSION_OVERLAY_ARTIFACT)
    if p40 is None:
        return None, None
    return _build_fusion_overlay_packet(p40), P40_FUSION_OVERLAY_ARTIFACT


# ── P44 operator narrative overlay ingest ─────────────────────────────────────


def _build_operator_narrative_packet(overlay: dict[str, Any]) -> dict[str, Any]:
    section_navigation: list[dict[str, Any]] = []
    for item in overlay.get("section_navigation", []):
        if not isinstance(item, dict):
            continue
        section_id = str(item.get("section_id", "")).strip()
        title = str(item.get("title", "")).strip()
        if not section_id or not title:
            continue
        section_navigation.append(
            {
                "section_id": section_id,
                "title": title,
                "status": str(item.get("status", "NOT_COMPUTABLE")),
                "index": int(item.get("index", 0)),
            }
        )

    overlay_cards: list[dict[str, Any]] = []
    for item in overlay.get("overlay_cards", []):
        if not isinstance(item, dict):
            continue
        card_id = str(item.get("card_id", "")).strip()
        title = str(item.get("title", "")).strip()
        if not card_id or not title:
            continue
        card: dict[str, Any] = {
            "card_id": card_id,
            "title": title,
        }
        if "status" in item and item["status"] is not None:
            card["status"] = str(item["status"])
        if "blocker_count" in item and item["blocker_count"] is not None:
            card["blocker_count"] = int(item["blocker_count"])
        blocker_summary = item.get("blocker_summary")
        if isinstance(blocker_summary, list):
            card["blocker_summary"] = [str(b) for b in blocker_summary if str(b).strip()]
        observed_fields = item.get("observed_fields")
        if isinstance(observed_fields, dict) and observed_fields:
            card["observed_fields"] = observed_fields
        overlay_cards.append(card)

    report_overlay_summary = overlay.get("report_overlay_summary")
    summary: dict[str, Any] = {}
    if isinstance(report_overlay_summary, dict):
        for key in (
            "report_final_status",
            "report_posture",
            "audit_final_status",
            "audit_posture",
            "blocker_count",
            "section_count",
        ):
            if key in report_overlay_summary and report_overlay_summary[key] is not None:
                summary[key] = report_overlay_summary[key]

    return {
        "packet_type": "OperatorNarrativeReportUIOverlay.v1",
        "final_status": str(overlay.get("final_status", "NOT_COMPUTABLE")),
        "overlay_posture": str(overlay.get("overlay_posture", "NOT_COMPUTABLE")),
        "report_overlay_summary": summary,
        "section_navigation": section_navigation,
        "overlay_cards": overlay_cards,
        "governance_flags": {
            "advisory_only": True,
            "projection_only": True,
        },
    }


def _load_operator_narrative() -> tuple[dict[str, Any] | None, str | None]:
    overlay = _load_safe(ROOT / OPERATOR_NARRATIVE_OVERLAY_ARTIFACT)
    if overlay is None:
        return None, None
    return _build_operator_narrative_packet(overlay), OPERATOR_NARRATIVE_OVERLAY_ARTIFACT


def _build_migration_runner_posture() -> tuple[dict[str, Any], str | None]:
    dashboard = _load_safe(ROOT / SUBSYSTEM_HEALTH_DASHBOARD_RECEIPT)
    if dashboard is None:
        return (
            {
                "source_status": "MISSING",
                "status": "NOT_COMPUTABLE",
                "migration_run_id": "NOT_COMPUTABLE",
                "requested_execution_result": "NOT_COMPUTABLE",
                "requested_execution_reason": (
                    "Subsystem health dashboard receipt is missing, so migration runner posture stays fail-closed."
                ),
                "safe_next_surface": "NOT_COMPUTABLE",
                "recommended_next_engineering_move": (
                    "Rebuild the subsystem health dashboard receipt before relying on live console posture."
                ),
                "blocked_action_count": 0,
                "blocked_action_sample": [],
                "stage_count": 0,
                "stage_posture_summary": {},
                "authority_granted": False,
            },
            None,
        )

    posture = dashboard.get("migration_runner_posture")
    if not isinstance(posture, dict):
        return (
            {
                "source_status": "NOT_COMPUTABLE",
                "status": "NOT_COMPUTABLE",
                "migration_run_id": "NOT_COMPUTABLE",
                "requested_execution_result": "NOT_COMPUTABLE",
                "requested_execution_reason": (
                    "Subsystem health dashboard receipt is malformed, so migration runner posture remains fail-closed."
                ),
                "safe_next_surface": "NOT_COMPUTABLE",
                "recommended_next_engineering_move": (
                    "Repair the subsystem health dashboard receipt shape before using it as a live console source."
                ),
                "blocked_action_count": 0,
                "blocked_action_sample": [],
                "stage_count": 0,
                "stage_posture_summary": {},
                "authority_granted": False,
            },
            SUBSYSTEM_HEALTH_DASHBOARD_RECEIPT,
        )

    stage_summary = posture.get("stage_posture_summary", {})
    blocked_sample = posture.get("blocked_action_sample", [])
    return (
        {
            "source_status": str(posture.get("source_status", "NOT_COMPUTABLE")),
            "status": str(posture.get("status", "NOT_COMPUTABLE")),
            "migration_run_id": str(posture.get("migration_run_id", "NOT_COMPUTABLE")),
            "requested_execution_result": str(
                posture.get("requested_execution_result", "NOT_COMPUTABLE")
            ),
            "requested_execution_reason": str(
                posture.get(
                    "requested_execution_reason",
                    "Migration runner posture is unavailable.",
                )
            ),
            "safe_next_surface": str(
                posture.get("safe_next_surface", "NOT_COMPUTABLE")
            ),
            "recommended_next_engineering_move": str(
                posture.get("recommended_next_engineering_move", "NOT_COMPUTABLE")
            ),
            "blocked_action_count": int(posture.get("blocked_action_count", 0)),
            "blocked_action_sample": (
                [str(item) for item in blocked_sample[:4]]
                if isinstance(blocked_sample, list)
                else []
            ),
            "stage_count": int(posture.get("stage_count", 0)),
            "stage_posture_summary": (
                {str(key): int(value) for key, value in stage_summary.items()}
                if isinstance(stage_summary, dict)
                else {}
            ),
            "authority_granted": False,
        },
        SUBSYSTEM_HEALTH_DASHBOARD_RECEIPT,
    )


def _build_combined_health_migration_artifact_posture() -> tuple[dict[str, Any], list[str]]:
    posture, observed_sources = build_combined_health_migration_artifact_posture(
        repo_root=ROOT
    )
    if _load_safe(ROOT / SUBSYSTEM_HEALTH_DASHBOARD_RECEIPT) is None:
        posture = {
            **posture,
            "source_status": "MISSING",
            "status": "NOT_COMPUTABLE",
            "health_status": "MISSING",
            "migration_runner_status": "NOT_COMPUTABLE",
            "requested_execution_result": "NOT_COMPUTABLE",
            "safe_next_surface": "NOT_COMPUTABLE",
            "authority_granted": False,
        }
        observed_sources = [
            source for source in observed_sources
            if source != SUBSYSTEM_HEALTH_DASHBOARD_RECEIPT
        ]
    return posture, observed_sources


def _build_migration_preflight_posture() -> tuple[dict[str, Any], str | None]:
    preflight = _load_safe(ROOT / CONTINUITY_NAMESPACE_MIGRATION_PREFLIGHT_RECEIPT)
    if preflight is None:
        return (
            {
                "source_status": "MISSING",
                "status": "NOT_COMPUTABLE",
                "check_count": 0,
                "pass_count": 0,
                "held_count": 0,
                "migration_runner_status": "NOT_COMPUTABLE",
                "alias_design_state": "NOT_COMPUTABLE",
                "valid_for_implementation": False,
                "blocked_action_count": 0,
                "blocked_action_sample": [],
                "recommended_next_engineering_move": (
                    "Rebuild the continuity namespace migration preflight receipt before relying on live console posture."
                ),
                "authority_granted": False,
            },
            None,
        )

    summary = preflight.get("preflight_summary")
    blocked_actions = preflight.get("blocked_actions", [])
    if not isinstance(summary, dict):
        return (
            {
                "source_status": "NOT_COMPUTABLE",
                "status": "NOT_COMPUTABLE",
                "check_count": 0,
                "pass_count": 0,
                "held_count": 0,
                "migration_runner_status": "NOT_COMPUTABLE",
                "alias_design_state": "NOT_COMPUTABLE",
                "valid_for_implementation": False,
                "blocked_action_count": 0,
                "blocked_action_sample": [],
                "recommended_next_engineering_move": (
                    "Repair the continuity namespace migration preflight receipt shape before projecting it."
                ),
                "authority_granted": False,
            },
            CONTINUITY_NAMESPACE_MIGRATION_PREFLIGHT_RECEIPT,
        )

    return (
        {
            "source_status": str(preflight.get("source_status", "NOT_COMPUTABLE")),
            "status": str(preflight.get("status", "NOT_COMPUTABLE")),
            "check_count": int(summary.get("check_count", 0)),
            "pass_count": int(summary.get("pass_count", 0)),
            "held_count": int(summary.get("held_count", 0)),
            "migration_runner_status": str(
                summary.get("migration_runner_status", "NOT_COMPUTABLE")
            ),
            "alias_design_state": str(
                summary.get("alias_design_state", "NOT_COMPUTABLE")
            ),
            "valid_for_implementation": False,
            "blocked_action_count": len(blocked_actions)
            if isinstance(blocked_actions, list)
            else 0,
            "blocked_action_sample": (
                [str(item) for item in blocked_actions[:4]]
                if isinstance(blocked_actions, list)
                else []
            ),
            "recommended_next_engineering_move": str(
                preflight.get("recommended_next_engineering_move", "NOT_COMPUTABLE")
            ),
            "authority_granted": False,
        },
        CONTINUITY_NAMESPACE_MIGRATION_PREFLIGHT_RECEIPT,
    )


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return sorted({str(item) for item in value if str(item).strip()})


def _source_status(payload: dict[str, Any] | None) -> str:
    return "OBSERVED" if payload is not None else "NOT_COMPUTABLE"


def _source_descriptor(key: str, payload: dict[str, Any] | None) -> dict[str, Any]:
    source_path = OPERATOR_PLATFORM_SOURCES[key]
    if Path(source_path).is_absolute():
        raise ValueError(f"FAIL_CLOSED: absolute source path is forbidden: {source_path}")
    content_hash: str | None = None
    if payload is not None:
        content_hash = hashlib.sha256((ROOT / source_path).read_bytes()).hexdigest()
    declared_hash = None if payload is None else payload.get(
        "canonical_hash", payload.get("packet_hash", payload.get("seal"))
    )
    return {
        "source_key": key,
        "path": source_path,
        "declared_canonical_hash": declared_hash if isinstance(declared_hash, str) else None,
        "content_sha256": content_hash,
        "integrity_state": "VERIFIED" if content_hash is not None else "NOT_COMPUTABLE",
    }


def _validate_temporal_diff_source(payload: dict[str, Any]) -> None:
    """Reject a present v1 artifact unless schema, authority, IDs, and hash agree."""
    try:
        from jsonschema import Draft202012Validator

        schema = json.loads(TEMPORAL_DIFF_SCHEMA_PATH.read_text(encoding="utf-8"))
        errors = sorted(
            Draft202012Validator(schema).iter_errors(payload),
            key=lambda error: list(error.path),
        )
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"FAIL_CLOSED: temporal diff schema unavailable: {exc}") from exc
    if errors:
        raise ValueError(
            f"FAIL_CLOSED: temporal diff schema violation: {errors[0].message}"
        )
    expected_authority = {
        "projection_only": True,
        "runtime_mutation_allowed": False,
        "promotion_allowed": False,
        "production_activation_allowed": False,
        "history_retention_allowed": False,
        "alerting_allowed": False,
        "scheduling_allowed": False,
    }
    if payload.get("authority") != expected_authority:
        raise ValueError("FAIL_CLOSED: temporal diff authority locks are malformed")
    unhashed = {key: value for key, value in payload.items() if key != "canonical_hash"}
    expected_hash = hashlib.sha256(
        json.dumps(
            unhashed, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("utf-8")
    ).hexdigest()
    if payload.get("canonical_hash") != expected_hash:
        raise ValueError("FAIL_CLOSED: temporal diff canonical hash mismatch")
    entries = payload.get("entries", [])
    expected_order = sorted(
        entries,
        key=lambda entry: (
            entry["category"], entry["surface"], entry["entity_id"],
            entry["field_path"], entry["operation"], entry["id"],
        ),
    )
    if entries != expected_order:
        raise ValueError("FAIL_CLOSED: temporal diff entries are not canonically ordered")
    entry_ids: set[str] = set()
    for entry in entries:
        identity = [
            entry["operation"], entry["category"], entry["entity_id"], entry["field_path"]
        ]
        expected_id = hashlib.sha256(
            json.dumps(identity, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        ).hexdigest()
        if entry["id"] != expected_id or entry["id"] in entry_ids:
            raise ValueError("FAIL_CLOSED: temporal diff entry identity mismatch")
        entry_ids.add(entry["id"])


def _section_envelope(
    payload: dict[str, Any],
    *,
    source_keys: list[str],
    source_payloads: dict[str, dict[str, Any] | None],
    validation_findings: list[str] | None = None,
) -> dict[str, Any]:
    findings = sorted(set(validation_findings or []))
    present_count = sum(source_payloads[key] is not None for key in source_keys)
    if present_count == 0:
        status = "NOT_COMPUTABLE"
        section_payload: dict[str, Any] | None = None
        reason = "All source artifacts for this section are missing or malformed."
    else:
        status = "PARTIAL" if present_count < len(source_keys) or findings else "AVAILABLE"
        section_payload = payload
        reason = None
    return {
        "status": status,
        "provenance": "OBSERVED" if present_count else "INFERRED",
        "source_artifacts": [_source_descriptor(key, source_payloads[key]) for key in source_keys],
        "payload": section_payload,
        "not_computable_reason": reason,
        "validation_findings": findings,
    }


def _build_operator_platform(
    systems: list[dict[str, Any]],
    operator_queue: list[dict[str, Any]],
    *,
    generated_at: str | None = None,
) -> tuple[dict[str, Any], list[str], dict[str, Any], dict[str, Any]]:
    payloads = {
        key: _load_safe(ROOT / path) for key, path in OPERATOR_PLATFORM_SOURCES.items()
    }
    observed_sources = sorted(
        OPERATOR_PLATFORM_SOURCES[key]
        for key, payload in payloads.items()
        if payload is not None
    )

    operator_console = payloads["operator_console"]
    surface_receipt = payloads["surface_receipt"]
    production_source = payloads["production_slice"]
    contract_source = payloads["contract_inventory"]
    graph_source = payloads["graph_render"]
    yggdrasil_source = payloads["yggdrasil"]
    temporal_source = payloads["temporal_diff"]
    if temporal_source is not None:
        _validate_temporal_diff_source(temporal_source)

    blockers = _string_list(
        operator_console.get("remaining_blockers", []) if operator_console else []
    )
    system_status = {
        "source_status": _source_status(operator_console),
        "stabilization_status": str(
            (surface_receipt or {}).get("parent_stabilization_status", "NOT_COMPUTABLE")
        ),
        "production_slice_status": str(
            (surface_receipt or {}).get("packet_status", "NOT_COMPUTABLE")
        ),
        "system_count": len(systems),
        "ready_system_count": sum(
            1 for system in systems if str(system.get("status", "")).startswith("READY")
        ),
        "work_items": sorted(
            [
                {
                    "id": str(item.get("action_id", "")),
                    "label": str(item.get("label", "")),
                    "status": str(item.get("status", "PENDING")),
                    "target": str(item.get("target_system", "")),
                }
                for item in operator_queue
            ],
            key=lambda item: (item["status"], item["id"]),
        ),
        "failures": blockers,
        "inherited_debt": blockers,
        "receipt_count": sum(len(system.get("ledger_receipts", [])) for system in systems),
        "operator_summary": _string_list(
            operator_console.get("operator_next_actions", []) if operator_console else []
        ),
    }

    topology_nodes: dict[str, dict[str, Any]] = {}
    topology_edges: dict[str, dict[str, Any]] = {}
    topology_findings: list[str] = []
    if graph_source:
        for raw in graph_source.get("nodes", []):
            if not isinstance(raw, dict):
                topology_findings.append("Excluded a malformed topology node that was not an object.")
                continue
            node_id = str(raw.get("node_id", "")).strip()
            if not node_id:
                topology_findings.append("Excluded a topology node with no stable node_id.")
                continue
            if node_id in topology_nodes:
                topology_findings.append(f"Excluded duplicate topology node id: {node_id}")
                continue
            topology_nodes[node_id] = {
                "id": node_id,
                "label": str(raw.get("label", raw.get("source_ref", node_id))),
                "entity_type": "PACKET",
                "status": str(raw.get("status", "NOT_COMPUTABLE")),
                "source_ref": str(raw.get("source_ref", "")),
                "provenance": str(raw.get("source_key", "aal_viz_graph_render")),
            }
        for raw in graph_source.get("edges", []):
            if not isinstance(raw, dict):
                continue
            edge_id = str(raw.get("edge_id", "")).strip()
            source = str(raw.get("source_node_id", "")).strip()
            target = str(raw.get("target_node_id", "")).strip()
            if edge_id and source and target:
                if edge_id in topology_edges:
                    topology_findings.append(f"Excluded duplicate topology edge id: {edge_id}")
                    continue
                topology_edges[edge_id] = {
                    "id": edge_id,
                    "source": source,
                    "target": target,
                    "relation": str(raw.get("category", "RELATED")),
                    "status": str(raw.get("status", "NOT_COMPUTABLE")),
                    "provenance": "aal_viz_graph_render",
                }
            else:
                topology_findings.append("Excluded a topology edge missing id or endpoint.")

    if yggdrasil_source:
        rune_map = yggdrasil_source.get("rune_to_pipelines", {})
        route_map = yggdrasil_source.get("pipeline_to_route", {})
        unbound = set(_string_list(yggdrasil_source.get("unbound_runes", [])))
        if isinstance(rune_map, dict):
            for rune, pipelines in sorted(rune_map.items()):
                rune_id = f"rune:{rune}"
                topology_nodes[rune_id] = {
                    "id": rune_id,
                    "label": str(rune),
                    "entity_type": "RUNE",
                    "status": "UNBOUND" if rune in unbound else "BOUND",
                    "source_ref": str(rune),
                    "provenance": OPERATOR_PLATFORM_SOURCES["yggdrasil"],
                }
                for pipeline in _string_list(pipelines):
                    pipeline_id = f"system:{pipeline}"
                    topology_nodes.setdefault(
                        pipeline_id,
                        {
                            "id": pipeline_id,
                            "label": pipeline,
                            "entity_type": "SYSTEM",
                            "status": "OBSERVED",
                            "source_ref": pipeline,
                            "provenance": OPERATOR_PLATFORM_SOURCES["yggdrasil"],
                        },
                    )
                    edge_id = f"binding:{rune}:{pipeline}"
                    topology_edges[edge_id] = {
                        "id": edge_id,
                        "source": rune_id,
                        "target": pipeline_id,
                        "relation": "BINDS",
                        "status": "OBSERVED",
                        "provenance": OPERATOR_PLATFORM_SOURCES["yggdrasil"],
                    }
        if isinstance(route_map, dict):
            for pipeline, route in sorted(route_map.items()):
                route_id = f"route:{route}"
                topology_nodes[route_id] = {
                    "id": route_id,
                    "label": str(route),
                    "entity_type": "ROUTE",
                    "status": "OBSERVED",
                    "source_ref": str(route),
                    "provenance": OPERATOR_PLATFORM_SOURCES["yggdrasil"],
                }
                edge_id = f"route-binding:{pipeline}:{route}"
                topology_edges[edge_id] = {
                    "id": edge_id,
                    "source": f"system:{pipeline}",
                    "target": route_id,
                    "relation": "ROUTES_TO",
                    "status": "OBSERVED",
                    "provenance": OPERATOR_PLATFORM_SOURCES["yggdrasil"],
                }

    for edge_id, edge in list(topology_edges.items()):
        if edge["source"] not in topology_nodes or edge["target"] not in topology_nodes:
            topology_findings.append(f"Excluded dangling topology edge: {edge_id}")
            del topology_edges[edge_id]

    topology = {
        "source_status": (
            "OBSERVED" if graph_source is not None or yggdrasil_source is not None
            else "NOT_COMPUTABLE"
        ),
        "nodes": sorted(topology_nodes.values(), key=lambda item: item["id"]),
        "edges": sorted(topology_edges.values(), key=lambda item: item["id"]),
    }

    topology_source_descriptors = {
        key: _source_descriptor(key, payloads[key])
        for key in YGGDRASIL_TOPOLOGY_SOURCE_KEYS
    }
    yggdrasil_topology = build_yggdrasil_topology(
        {key: payloads[key] for key in YGGDRASIL_TOPOLOGY_SOURCE_KEYS},
        {
            key: OPERATOR_PLATFORM_SOURCES[key]
            for key in YGGDRASIL_TOPOLOGY_SOURCE_KEYS
        },
        {
            key: topology_source_descriptors[key]["content_sha256"]
            for key in YGGDRASIL_TOPOLOGY_SOURCE_KEYS
        },
        generated_at=generated_at or _utc_now(),
    )
    topology = operator_topology_payload(yggdrasil_topology)
    topology_findings = list(yggdrasil_topology["validation_findings"])

    production_slice = {
        "source_status": _source_status(production_source),
        "classification": str(
            (production_source or {}).get("classification", "NOT_COMPUTABLE")
        ),
        "entrypoint": str((production_source or {}).get("entrypoint", "NOT_COMPUTABLE")),
        "invocation": str((production_source or {}).get("invocation", "NOT_COMPUTABLE")),
        "orchestration": _string_list(
            (production_source or {}).get("orchestration_path", [])
        ),
        "validators": _string_list((production_source or {}).get("runtime_validators", [])),
        "execution_flow": [
            str(item) for item in (production_source or {}).get("execution_flow", [])
            if str(item).strip()
        ],
        "artifacts": _string_list((production_source or {}).get("artifact_paths", [])),
        "receipts": (
            [OPERATOR_PLATFORM_SOURCES["surface_receipt"]]
            if surface_receipt is not None else []
        ),
        "excluded_surfaces": _string_list(
            (production_source or {}).get("excluded_surfaces", [])
        ),
        "unresolved_links": _string_list(
            (production_source or {}).get("unresolved_links", [])
        ),
        "external_calls": bool((production_source or {}).get("external_calls", False)),
        "persistence_behavior": str(
            (production_source or {}).get("persistence_behavior", "NOT_COMPUTABLE")
        ),
    }

    contracts: list[dict[str, Any]] = []
    if contract_source:
        for raw in contract_source.get("contracts", []):
            if not isinstance(raw, dict):
                continue
            ownership = raw.get("ownership", {})
            if not isinstance(ownership, dict):
                ownership = {}
            contract_id = str(raw.get("contract_id", "")).strip()
            if not contract_id:
                continue
            contracts.append(
                {
                    "id": contract_id,
                    "language": str(raw.get("language", "unknown")),
                    "version": str(raw.get("version", "UNRESOLVED")),
                    "owner": str(ownership.get("module", ownership.get("file", "UNRESOLVED"))),
                    "owner_resolved": bool(raw.get("owner_resolved", False)),
                    "validation_mode": str(raw.get("validation_mode", "NOT_COMPUTABLE")),
                    "production_reachability": str(
                        raw.get("production_reachability", "NOT_COMPUTABLE")
                    ),
                    "producers": _string_list(raw.get("producers", [])),
                    "validators": _string_list(raw.get("validators", [])),
                    "consumers": _string_list(raw.get("consumers", [])),
                }
            )
    contracts.sort(key=lambda item: item["id"])
    contract_graph = {
        "source_status": _source_status(contract_source),
        "contract_count": len(contracts),
        "unowned_count": sum(1 for item in contracts if not item["owner_resolved"]),
        "unvalidated_count": sum(1 for item in contracts if not item["validators"]),
        "contracts": contracts,
    }

    evidence_index: list[dict[str, Any]] = []
    evidence_findings: list[str] = []
    for key in (
        "surface_receipt", "contract_receipt", "operator_console", "graph_render",
        "yggdrasil", "temporal_diff",
    ):
        payload = payloads[key]
        source_path = OPERATOR_PLATFORM_SOURCES[key]
        if payload is None:
            evidence_index.append(
                {
                    "id": key,
                    "source_status": "NOT_COMPUTABLE",
                    "source_path": source_path,
                    "canonical_hash": None,
                    "status": "MISSING",
                    "inputs": [],
                    "outputs": [],
                    "schemas": [],
                    "links": [],
                    "fail_closed_reason": "Source artifact is missing or malformed.",
                }
            )
            continue
        raw_canonical_hash = payload.get(
            "canonical_hash", payload.get("packet_hash", payload.get("seal"))
        )
        if raw_canonical_hash is not None and not isinstance(raw_canonical_hash, str):
            evidence_findings.append(
                f"Normalized non-scalar canonical hash to NOT_COMPUTABLE for source: {source_path}"
            )
            raw_canonical_hash = None
        evidence_index.append(
            {
                "id": str(payload.get("packet_id", payload.get("artifact_id", key))),
                "source_status": "OBSERVED",
                "source_path": source_path,
                "canonical_hash": raw_canonical_hash,
                "status": str(
                    payload.get("final_status", payload.get("packet_status", payload.get("status", "OBSERVED")))
                ),
                "inputs": _string_list(payload.get("source_artifacts", payload.get("source_entries", []))),
                "outputs": _string_list(payload.get("artifact_paths", [])),
                "schemas": _string_list([payload.get("schema", payload.get("schema_version", ""))]),
                "links": _string_list(payload.get("remaining_blockers", [])),
                "fail_closed_reason": None,
            }
        )
    evidence_index.sort(key=lambda item: item["id"])

    diff_entries: list[dict[str, Any]] = []
    temporal_findings: list[str] = []
    allowed_operations = {"ADDED", "REMOVED", "CHANGED", "NOT_COMPUTABLE"}
    allowed_categories = {
        "TOPOLOGY_NODE", "TOPOLOGY_EDGE", "CONTRACT_FIELD", "OWNERSHIP",
        "VALIDATOR_STATE", "RECEIPT", "PACKET", "SOURCE_INTEGRITY",
        "SECTION_STATUS",
    }
    if temporal_source:
        for index, raw in enumerate(temporal_source.get("entries", [])):
            if not isinstance(raw, dict):
                temporal_findings.append("Excluded a malformed temporal entry that was not an object.")
                continue
            operation = str(raw.get("operation", "NOT_COMPUTABLE")).upper()
            if operation not in allowed_operations:
                temporal_findings.append(f"Mapped unsupported temporal operation to NOT_COMPUTABLE: {operation}")
                operation = "NOT_COMPUTABLE"
            category = str(raw.get("category", "SECTION_STATUS")).upper()
            if category not in allowed_categories:
                temporal_findings.append(
                    f"Excluded unsupported temporal category: {category}"
                )
                continue
            diff_entries.append(
                {
                    "id": str(raw.get("id", f"change-{index:04d}")),
                    "operation": operation,
                    "category": category,
                    "impact": str(raw.get("impact", "NEUTRAL")),
                    "surface": str(raw.get("surface", "UNKNOWN")),
                    "entity_id": str(raw.get("entity_id", "UNKNOWN")),
                    "summary": (
                        f"{operation} {category.lower().replace('_', ' ')}: "
                        f"{raw.get('entity_id', 'UNKNOWN')}"
                    ),
                    "severity": (
                        "WARNING"
                        if raw.get("impact") in {"WEAKENED", "NOT_COMPUTABLE"}
                        else "INFO"
                    ),
                    "field_path": str(raw.get("field_path", "")),
                    "prior_value": raw.get("prior_value"),
                    "current_value": raw.get("current_value"),
                    "provenance": str(raw.get("provenance", "OBSERVED")),
                    "prior_generation_id": raw.get("prior_generation_id"),
                    "current_generation_id": raw.get("current_generation_id"),
                    "prior_evidence_status": str(
                        raw.get("prior_evidence_status", "NOT_COMPUTABLE")
                    ),
                    "current_evidence_status": str(
                        raw.get("current_evidence_status", "NOT_COMPUTABLE")
                    ),
                    "reason_code": raw.get("reason_code"),
                    "source_keys": _string_list(raw.get("source_keys", [])),
                }
            )
    diff_entries.sort(key=lambda item: (item["category"], item["surface"], item["id"]))
    temporal_diff = {
        "source_status": _source_status(temporal_source),
        "status": str((temporal_source or {}).get("status", "NOT_COMPUTABLE")),
        "prior_generation_id": (
            (temporal_source or {}).get("prior_generation", {}).get("generation_id")
            if isinstance((temporal_source or {}).get("prior_generation"), dict)
            else None
        ),
        "current_generation_id": (
            (temporal_source or {}).get("current_generation", {}).get("generation_id")
            if isinstance((temporal_source or {}).get("current_generation"), dict)
            else None
        ),
        "comparison_scope": _string_list(
            (temporal_source or {}).get("comparison_scope", [])
        ),
        "out_of_scope": _string_list(
            (temporal_source or {}).get("out_of_scope", [])
        ),
        "category_counts": dict(
            (temporal_source or {}).get("summary", {}).get("category_counts", {})
            if isinstance((temporal_source or {}).get("summary"), dict)
            else {}
        ),
        "total_change_count": int(
            (temporal_source or {}).get("summary", {}).get("total_change_count", 0)
            if isinstance((temporal_source or {}).get("summary"), dict)
            else 0
        ),
        "not_computable_count": int(
            (temporal_source or {}).get("summary", {}).get("not_computable_count", 0)
            if isinstance((temporal_source or {}).get("summary"), dict)
            else 0
        ),
        "topology_change_count": sum(
            1 for item in diff_entries
            if item["category"] in {"TOPOLOGY_NODE", "TOPOLOGY_EDGE"}
            and item["operation"] != "NOT_COMPUTABLE"
        ),
        "lineage_shift_count": 0,
        "queue_delta_count": 0,
        "transport_delta_count": 0,
        "operator_summary": (
            "No evidence-bound changes were observed in the current generation."
            if temporal_source is not None and not diff_entries
            else f"{len(diff_entries)} evidence-bound changes require review."
        ),
        "entries": diff_entries,
        "remaining_blockers": [
            str(reason.get("detail", reason.get("reason_code", "NOT_COMPUTABLE")))
            for reason in (temporal_source or {}).get("not_computable_reasons", [])
            if isinstance(reason, dict)
        ],
    }

    source_descriptors = [
        _source_descriptor(key, payloads[key]) for key in sorted(OPERATOR_PLATFORM_SOURCES)
    ]
    platform = {
            "schema_version": "AALViz.OperatorPlatformProjection.v0.2",
            "generation": {
                "generated_at": generated_at or _utc_now(),
                "generated_by": GENERATED_BY,
                "source_bundle_schema_version": SCHEMA_VERSION,
            },
            "authority": dict(AUTHORITY),
            "projection_only": True,
            "source_artifacts": source_descriptors,
            "system_status": _section_envelope(
                system_status,
                source_keys=["operator_console", "surface_receipt"],
                source_payloads=payloads,
            ),
            "topology": _section_envelope(
                topology,
                source_keys=list(YGGDRASIL_TOPOLOGY_SOURCE_KEYS),
                source_payloads=payloads,
                validation_findings=topology_findings,
            ),
            "production_slice": _section_envelope(
                production_slice,
                source_keys=["production_slice", "surface_receipt"],
                source_payloads=payloads,
            ),
            "contract_graph": _section_envelope(
                contract_graph,
                source_keys=["contract_inventory", "contract_receipt"],
                source_payloads=payloads,
            ),
            "evidence_index": _section_envelope(
                {"records": evidence_index},
                source_keys=sorted(OPERATOR_PLATFORM_SOURCES),
                source_payloads=payloads,
                validation_findings=evidence_findings,
            ),
            "temporal_diff": _section_envelope(
                temporal_diff,
                source_keys=["temporal_diff"],
                source_payloads=payloads,
                validation_findings=temporal_findings,
            ),
        }
    operator_generation_id = generation_id(platform)
    temporal_descriptor = next(
        item for item in source_descriptors if item["source_key"] == "temporal_diff"
    )
    yggdrasil_topology = bind_yggdrasil_topology(
        yggdrasil_topology,
        operator_generation_id,
        temporal_diff=temporal_source,
        temporal_source_path=OPERATOR_PLATFORM_SOURCES["temporal_diff"],
        temporal_content_sha256=temporal_descriptor["content_sha256"],
    )
    validate_yggdrasil_topology(
        yggdrasil_topology, YGGDRASIL_TOPOLOGY_SCHEMA_PATH
    )
    topology_bytes = json.dumps(
        yggdrasil_topology, indent=2, sort_keys=True
    ).encode("utf-8")
    yggdrasil_topology_integrity = evaluate_yggdrasil_topology_integrity(
        yggdrasil_topology,
        temporal_source,
        topology_path=str(YGGDRASIL_TOPOLOGY_OUTPUT_PATH.relative_to(ROOT)),
        temporal_diff_path=OPERATOR_PLATFORM_SOURCES["temporal_diff"],
        topology_content_sha256=hashlib.sha256(topology_bytes).hexdigest(),
        temporal_diff_content_sha256=temporal_descriptor["content_sha256"],
        generated_at=generated_at or _utc_now(),
    )
    validate_yggdrasil_topology_integrity(
        yggdrasil_topology_integrity,
        YGGDRASIL_TOPOLOGY_INTEGRITY_SCHEMA_PATH,
        topology=yggdrasil_topology,
    )
    return (
        platform,
        observed_sources,
        yggdrasil_topology,
        yggdrasil_topology_integrity,
    )


# ── Main ─────────────────────────────────────────────────────────────────────


def _load_delta_intelligence_sidecar(
    topology: Mapping[str, Any],
) -> dict[str, Any] | None:
    """Load only an already-published, current-generation advisory sidecar."""
    if not YGGDRASIL_TOPOLOGY_DELTA_INTELLIGENCE_OUTPUT_PATH.exists():
        return None
    try:
        value = json.loads(
            YGGDRASIL_TOPOLOGY_DELTA_INTELLIGENCE_OUTPUT_PATH.read_text(
                encoding="utf-8"
            )
        )
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(
            f"FAIL_CLOSED: malformed topology delta intelligence sidecar: {exc}"
        ) from exc
    if not isinstance(value, dict):
        raise ValueError("FAIL_CLOSED: topology delta intelligence must be an object")
    validate_yggdrasil_topology_delta_intelligence(
        value, YGGDRASIL_TOPOLOGY_DELTA_INTELLIGENCE_SCHEMA_PATH
    )
    current_id = value["generation"]["current_topology_generation_id"]
    topology_id = topology["generation"]["topology_generation_id"]
    if current_id != topology_id:
        return None
    return value


def _load_advisory_alerts_sidecar(
    delta_intelligence: Mapping[str, Any] | None,
    topology: Mapping[str, Any],
    operator_platform: Mapping[str, Any],
) -> dict[str, Any] | None:
    """Load only an already-published alert sidecar bound to current evidence."""
    if (
        delta_intelligence is None
        or not ROUTE_RECEIPT_ADVISORY_ALERTS_OUTPUT_PATH.exists()
    ):
        return None
    try:
        value = json.loads(
            ROUTE_RECEIPT_ADVISORY_ALERTS_OUTPUT_PATH.read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(
            f"FAIL_CLOSED: malformed advisory alerts sidecar: {exc}"
        ) from exc
    if not isinstance(value, dict):
        raise ValueError("FAIL_CLOSED: advisory alerts sidecar must be an object")
    validate_route_receipt_advisory_alerts(
        value, ROUTE_RECEIPT_ADVISORY_ALERTS_SCHEMA_PATH
    )
    generation = value["generation"]
    if (
        generation["delta_generation_id"]
        != delta_intelligence["generation"]["delta_generation_id"]
        or generation["current_topology_generation_id"]
        != topology["generation"]["topology_generation_id"]
        or generation["current_operator_platform_generation_id"]
        != generation_id(operator_platform)
    ):
        return None
    return value


def build_bundle() -> dict[str, Any]:
    generated_at = _utc_now()
    systems: list[dict[str, Any]] = []
    all_source_artifacts: list[str] = []

    for op_id, cfg in OPERATOR_DEFS.items():
        proj = _build_operator_projection(op_id, cfg)
        all_source_artifacts.extend(proj.pop("_source_artifacts", []))
        systems.append(proj)

    operator_queue = _build_operator_queue(systems)
    fusion_overlay, fusion_source = _load_fusion_overlay()
    if fusion_source is not None:
        all_source_artifacts.append(fusion_source)
    operator_narrative_report, narrative_source = _load_operator_narrative()
    if narrative_source is not None:
        all_source_artifacts.append(narrative_source)
    migration_runner_posture, migration_source = _build_migration_runner_posture()
    if migration_source is not None:
        all_source_artifacts.append(migration_source)
    migration_preflight_posture, preflight_source = _build_migration_preflight_posture()
    if preflight_source is not None:
        all_source_artifacts.append(preflight_source)
    combined_health_migration_artifact_posture, combined_sources = (
        _build_combined_health_migration_artifact_posture()
    )
    all_source_artifacts.extend(combined_sources)
    (
        operator_platform,
        operator_platform_sources,
        yggdrasil_topology,
        yggdrasil_topology_integrity,
    ) = _build_operator_platform(systems, operator_queue, generated_at=generated_at)
    all_source_artifacts.extend(operator_platform_sources)
    yggdrasil_topology_delta_intelligence = _load_delta_intelligence_sidecar(
        yggdrasil_topology
    )
    if yggdrasil_topology_delta_intelligence is not None:
        all_source_artifacts.append(
            str(YGGDRASIL_TOPOLOGY_DELTA_INTELLIGENCE_OUTPUT_PATH.relative_to(ROOT))
        )
    route_receipt_advisory_alerts = _load_advisory_alerts_sidecar(
        yggdrasil_topology_delta_intelligence,
        yggdrasil_topology,
        operator_platform,
    )
    if route_receipt_advisory_alerts is not None:
        all_source_artifacts.append(
            str(ROUTE_RECEIPT_ADVISORY_ALERTS_OUTPUT_PATH.relative_to(ROOT))
        )

    bundle: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at,
        "generated_by": GENERATED_BY,
        "authority": AUTHORITY,
        "source_mode": "LIVE_ARTIFACT_BUNDLE",
        "source_artifacts": sorted(set(all_source_artifacts)),
        "fail_closed_reason": None,
        "systems": systems,
        "operator_queue": operator_queue,
        "migration_runner_posture": migration_runner_posture,
        "migration_preflight_posture": migration_preflight_posture,
        "combined_health_migration_artifact_posture": (
            combined_health_migration_artifact_posture
        ),
        "operator_platform": operator_platform,
        "yggdrasil_topology": yggdrasil_topology,
        "yggdrasil_topology_integrity": yggdrasil_topology_integrity,
    }
    if yggdrasil_topology_delta_intelligence is not None:
        bundle["yggdrasil_topology_delta_intelligence"] = (
            yggdrasil_topology_delta_intelligence
        )
    if route_receipt_advisory_alerts is not None:
        bundle["route_receipt_advisory_alerts"] = route_receipt_advisory_alerts
    if fusion_overlay is not None:
        bundle["fusion_overlay"] = fusion_overlay
    if operator_narrative_report is not None:
        bundle["operator_narrative_report"] = operator_narrative_report
    return bundle


def _validate_bundle(bundle: dict[str, Any]) -> None:
    """Fail closed if authority invariants are violated."""
    auth = bundle.get("authority", {})
    if auth.get("projection_only") is not True:
        raise ValueError("FAIL_CLOSED: authority.projection_only must be true")
    if auth.get("runtime_mutation_allowed") is not False:
        raise ValueError("FAIL_CLOSED: authority.runtime_mutation_allowed must be false")
    if auth.get("promotion_allowed") is not False:
        raise ValueError("FAIL_CLOSED: authority.promotion_allowed must be false")
    if auth.get("production_activation_allowed") is not False:
        raise ValueError("FAIL_CLOSED: authority.production_activation_allowed must be false")
    if not bundle.get("systems"):
        raise ValueError("FAIL_CLOSED: systems list is empty")
    platform = bundle.get("operator_platform", {})
    if platform.get("projection_only") is not True:
        raise ValueError("FAIL_CLOSED: operator_platform.projection_only must be true")
    try:
        from jsonschema import Draft202012Validator

        schema = json.loads(OPERATOR_PLATFORM_SCHEMA_PATH.read_text(encoding="utf-8"))
        Draft202012Validator(schema).validate(platform)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"FAIL_CLOSED: operator platform schema unavailable: {exc}") from exc
    except Exception as exc:
        if exc.__class__.__module__.startswith("jsonschema"):
            raise ValueError(f"FAIL_CLOSED: operator platform schema violation: {exc.message}") from exc
        raise
    topology = bundle.get("yggdrasil_topology")
    if topology is not None:
        validate_yggdrasil_topology(topology, YGGDRASIL_TOPOLOGY_SCHEMA_PATH)
    integrity = bundle.get("yggdrasil_topology_integrity")
    if integrity is not None:
        validate_yggdrasil_topology_integrity(
            integrity,
            YGGDRASIL_TOPOLOGY_INTEGRITY_SCHEMA_PATH,
            topology=topology,
        )
    delta_intelligence = bundle.get("yggdrasil_topology_delta_intelligence")
    if delta_intelligence is not None:
        validate_yggdrasil_topology_delta_intelligence(
            delta_intelligence,
            YGGDRASIL_TOPOLOGY_DELTA_INTELLIGENCE_SCHEMA_PATH,
        )
        if (
            delta_intelligence["generation"]["current_topology_generation_id"]
            != topology["generation"]["topology_generation_id"]
        ):
            raise ValueError(
                "FAIL_CLOSED: topology delta intelligence generation is stale"
            )
    advisory_alerts = bundle.get("route_receipt_advisory_alerts")
    if advisory_alerts is not None:
        validate_route_receipt_advisory_alerts(
            advisory_alerts, ROUTE_RECEIPT_ADVISORY_ALERTS_SCHEMA_PATH
        )
        if delta_intelligence is None or (
            advisory_alerts["generation"]["delta_generation_id"]
            != delta_intelligence["generation"]["delta_generation_id"]
        ):
            raise ValueError(
                "FAIL_CLOSED: advisory alerts delta generation is stale"
            )
        if (
            advisory_alerts["generation"]["current_topology_generation_id"]
            != topology["generation"]["topology_generation_id"]
            or advisory_alerts["generation"][
                "current_operator_platform_generation_id"
            ]
            != generation_id(platform)
        ):
            raise ValueError(
                "FAIL_CLOSED: advisory alerts current generation binding is stale"
            )


def main() -> int:
    try:
        bundle = build_bundle()
        _validate_bundle(bundle)
    except ValueError as exc:
        sys.stderr.write(f"ERROR: {exc}\n")
        fail_closed: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "generated_at": _utc_now(),
            "generated_by": GENERATED_BY,
            "authority": AUTHORITY,
            "source_mode": "FAIL_CLOSED",
            "source_artifacts": [],
            "fail_closed_reason": str(exc),
            "systems": [],
            "operator_queue": [],
        }
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(
            json.dumps(fail_closed, indent=2, sort_keys=True), encoding="utf-8"
        )
        return 1

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(bundle, indent=2, sort_keys=True), encoding="utf-8"
    )
    YGGDRASIL_TOPOLOGY_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    YGGDRASIL_TOPOLOGY_OUTPUT_PATH.write_text(
        json.dumps(bundle["yggdrasil_topology"], indent=2, sort_keys=True),
        encoding="utf-8",
    )
    YGGDRASIL_TOPOLOGY_INTEGRITY_OUTPUT_PATH.write_text(
        json.dumps(
            bundle["yggdrasil_topology_integrity"], indent=2, sort_keys=True
        ),
        encoding="utf-8",
    )
    sys.stdout.write(
        f"OK: wrote {len(bundle['systems'])} systems -> {OUTPUT_PATH.relative_to(ROOT)}; "
        f"topology -> {YGGDRASIL_TOPOLOGY_OUTPUT_PATH.relative_to(ROOT)}; "
        "integrity -> "
        f"{YGGDRASIL_TOPOLOGY_INTEGRITY_OUTPUT_PATH.relative_to(ROOT)}\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
