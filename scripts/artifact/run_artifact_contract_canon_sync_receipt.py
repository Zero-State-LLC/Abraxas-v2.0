from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import write_canonical_json

from scripts.artifact import run_artifact_contract_global_closure_audit as closure_audit
from scripts.artifact import run_artifact_contract_post_closure_operator_receipt as operator_receipt


def _load(path: str) -> Any:
    return json.loads(Path(path).read_text())


def build() -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    closure_path = "out/contracts/artifact_contract_global_closure_audit_report.latest.json"
    operator_path = "out/contracts/artifact_contract_post_closure_operator_receipt_report.latest.json"
    required = [closure_path, operator_path, "out/projections/aal_viz.latest.json", "out/validation/latest.json"]
    missing = [p for p in required if not Path(p).exists()]

    closure = _load(closure_path) if closure_path not in missing else {}
    operator = _load(operator_path) if operator_path not in missing else {}
    viz = _load("out/projections/aal_viz.latest.json") if "out/projections/aal_viz.latest.json" not in missing else {}

    if closure.get("status") not in {"passed", "missing"}:
        _, closure, _, _ = closure_audit.build()
    if operator.get("status") not in {"passed", "missing"}:
        _, operator, _ = operator_receipt.build()

    source_closure_status = closure.get("status", "missing")
    source_operator_status = operator.get("status", "missing")
    authority = closure.get("authority_invariant_details", {})
    authority_ok = (
        authority.get("projection_only") is True
        and authority.get("inference_authority") is False
        and authority.get("authority_leak_detected") is False
        and authority.get("autonomous_approval") is False
        and authority.get("execution_authority") is False
        and authority.get("runtime_mutation_authority") is False
        and authority.get("doctrine_mutation_authority") is False
        and authority.get("inventory_suppression_authority") is False
    )
    viz_ok = viz.get("projection_only", True) and viz.get("inference_authority", False) is False
    ready = source_closure_status == "passed" and source_operator_status == "passed"

    allowed = [
        "notion_canon_index_update_manual",
        "operator_dashboard_projection_refresh",
        "release_notes_generation",
        "stabilization_monitoring",
        "documentation_index_update",
        "final_state_attestation",
        "canon_snapshot_export",
    ]
    forbidden = [
        "autonomous_execution",
        "autonomous_approval",
        "runtime_mutation",
        "doctrine_mutation",
        "inventory_suppression",
        "projection_authority_escalation",
        "silent_gap_suppression",
        "unreviewed_queue_reopening",
        "unverified_notion_write",
    ]

    status = "passed" if (not missing and ready and authority_ok and viz_ok) else "failed"
    payload = {
        "schema": "ArtifactContractCanonSyncReceipt.v1",
        "generated_by": "RUN_ABRAXAS_ARTIFACT_CONTRACT_CANON_SYNC_RECEIPT_BATCH_021",
        "status": status,
        "sync_type": "non_mutating_readiness_receipt",
        "sync_scope": [
            "artifact_contract_repair_sequence",
            "global_closure_audit",
            "post_closure_operator_receipt",
            "authority_posture",
            "aal_viz_projection_posture",
        ],
        "source_closure_status": source_closure_status,
        "source_operator_receipt_status": source_operator_status,
        "sealed_sequence": "ABRAXAS_ARTIFACT_CONTRACT_REPAIR_SEQUENCE_P0_TO_P2C_D5 = SEALED",
        "canon_reflection_ready": ready,
        "notion_reflection_ready": ready,
        "notion_sync_performed": False,
        "required_artifacts_present_count": closure.get("required_artifacts_present", 0),
        "missing_artifacts_count": len(closure.get("missing_artifacts", missing)),
        "gap_count": closure.get("gap_count", 1),
        "critical_gap_count": closure.get("critical_gap_count", 1),
        "queue_counts": closure.get("queue_counts", {}),
        "queue_closure_summary": closure.get("queue_closure_summary", {}),
        "authority_posture": authority,
        "aal_viz_posture": {"projection_only": viz.get("projection_only", True), "inference_authority": viz.get("inference_authority", False)},
        "validation_surface_ok": closure.get("validation_surface_ok", False),
        "human_approval_nonexecuting": closure.get("human_approval_nonexecuting", False),
        "allowed_next_actions": allowed,
        "forbidden_actions": forbidden,
    }
    payload["canon_sync_hash"] = "sha256:" + hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()

    actions = ([{"action": a, "allowed": True} for a in allowed] + [{"action": a, "allowed": False} for a in forbidden])
    return payload, dict(payload), actions


def main() -> None:
    payload, report, actions = build()
    write_canonical_json("out/contracts/artifact_contract_canon_sync_receipt.latest.json", payload)
    write_canonical_json("out/contracts/artifact_contract_canon_sync_receipt_report.latest.json", report)
    write_canonical_json("out/contracts/artifact_contract_canon_sync_receipt_actions.latest.json", actions)


if __name__ == "__main__":
    main()
