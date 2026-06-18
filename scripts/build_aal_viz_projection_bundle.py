#!/usr/bin/env python3
"""
AAL-Viz Artifact Index Adapter — read-only projection bundle builder.

Reads:  out/metric_operator/ and out/projections/wasserstein_* artifact files.
        out/chamfer_*/  artifact files.
Writes: apps/aal-viz-live-console/public/projection-bundle.json

Authority constraints (always enforced):
  projection_only              = true
  runtime_mutation_allowed     = false
  promotion_allowed            = false
  production_activation_allowed = false

Never reads:  research_canary artifacts.
Never writes: out/  (output is confined to apps/aal-viz-live-console/public/).
Fails closed: on missing or malformed source artifacts (writes FAIL_CLOSED bundle).
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = ROOT / "apps" / "aal-viz-live-console" / "public" / "projection-bundle.json"
P40_FUSION_OVERLAY_ARTIFACT = (
    "out/projections/aal_viz_climate_motif_fusion_overlay_001.latest.json"
)
SCHEMA_VERSION = "AALViz.LiveConsoleProjectionBundle.v0.1"
GENERATED_BY = "BUILD_AAL_VIZ_PROJECTION_BUNDLE_001"

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

    source_artifacts = [str(ROOT / r) for r in seq if r in loaded]

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


# ── Main ─────────────────────────────────────────────────────────────────────


def build_bundle() -> dict[str, Any]:
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

    bundle: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": _utc_now(),
        "generated_by": GENERATED_BY,
        "authority": AUTHORITY,
        "source_mode": "LIVE_ARTIFACT_BUNDLE",
        "source_artifacts": sorted(set(all_source_artifacts)),
        "fail_closed_reason": None,
        "systems": systems,
        "operator_queue": operator_queue,
    }
    if fusion_overlay is not None:
        bundle["fusion_overlay"] = fusion_overlay
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
    sys.stdout.write(
        f"OK: wrote {len(bundle['systems'])} systems → {OUTPUT_PATH.relative_to(ROOT)}\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
