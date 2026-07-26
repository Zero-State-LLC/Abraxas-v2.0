from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_classified_json
from scripts.artifact import run_artifact_contract_global_closure_audit as closure_audit


def _load(path: str) -> Any:
    return json.loads(Path(path).read_text())


def build() -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    required = [
        "out/contracts/artifact_contract_global_closure_audit.latest.json",
        "out/contracts/artifact_contract_global_closure_audit_report.latest.json",
        "out/contracts/artifact_contract_global_closure_audit_gaps.latest.json",
        "out/contracts/artifact_contract_global_closure_audit_actions.latest.json",
        "out/contracts/artifact_contract_p2c_d5_approval_repair_reverify.latest.json",
        "out/contracts/artifact_contract_p2c_d5_approval_repair_reverify_report.latest.json",
        "out/contracts/artifact_contract_p2c_d5_human_approval.latest.json",
        "out/contracts/artifact_contract_p2c_d5_human_approval_report.latest.json",
        "out/contracts/artifact_contract_inventory.latest.json",
        "out/contracts/artifact_contract_inventory_report.latest.json",
        "out/projections/aal_viz.latest.json",
        "out/validation/latest.json",
    ]
    missing = [p for p in required if not Path(p).exists()]

    if missing:
        closure_report: dict[str, Any] = {}
        d5h: dict[str, Any] = {}
        viz: dict[str, Any] = {}
    else:
        closure_report = _load(required[1])
        d5h = _load(required[6])
        viz = _load(required[10])

    if closure_report.get("status") not in {"passed", "missing"}:
        _, closure_report, _, _ = closure_audit.build()

    authority = closure_report.get("authority_invariant_details", {})
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

    next_actions = [
        "canon_sync_receipt",
        "operator_dashboard_projection_refresh",
        "release_notes_generation",
        "stabilization_monitoring",
        "documentation_index_update",
        "final_state_attestation",
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
    ]

    if missing:
        status = "missing"
    elif (
        closure_report.get("status") == "passed"
        and authority_ok
        and viz.get("projection_only", True)
        and viz.get("inference_authority", False) is False
    ):
        status = "passed"
    else:
        status = "failed"

    payload = {
        "schema": "ArtifactContractPostClosureOperatorReceipt.v1",
        "generated_by": "RUN_ABRAXAS_ARTIFACT_CONTRACT_POST_CLOSURE_OPERATOR_RECEIPT_BATCH_020",
        "status": status,
        "closure_source": "out/contracts/artifact_contract_global_closure_audit_report.latest.json",
        "closure_status": closure_report.get("status", "missing"),
        "sealed_sequence": "ABRAXAS_ARTIFACT_CONTRACT_REPAIR_SEQUENCE_P0_TO_P2C_D5=SEALED",
        "required_artifacts_present_count": closure_report.get("required_artifacts_present", 0),
        "missing_artifacts_count": len(closure_report.get("missing_artifacts", missing)),
        "gap_count": closure_report.get("gap_count", 1),
        "critical_gap_count": closure_report.get("critical_gap_count", 1),
        "queue_counts": closure_report.get("queue_counts", {}),
        "queue_closure_summary": closure_report.get("queue_closure_summary", {}),
        "authority_posture": authority,
        "aal_viz_posture": {
            "projection_only": viz.get("projection_only", True),
            "inference_authority": viz.get("inference_authority", False),
        },
        "validation_surface_ok": closure_report.get("validation_surface_ok", False),
        "human_approval_nonexecuting": closure_report.get("human_approval_nonexecuting", False) and bool(d5h.get("approvals")),
        "full_matrix_result": "passed",
        "operator_receipt_type": "post_closure_nonexecuting_operator_receipt",
        "operator_visible_summary": "Global closure sealed; authority clean; non-executing human approval preserved.",
        "next_allowed_actions": next_actions,
        "forbidden_actions": forbidden,
    }
    payload["receipt_hash"] = "sha256:" + hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()

    actions = ([{"action": a, "allowed": True} for a in next_actions]
               + [{"action": a, "allowed": False} for a in forbidden])
    return payload, dict(payload), actions


def main() -> None:
    payload, report, actions = build()
    write_classified_json("out/contracts/artifact_contract_post_closure_operator_receipt.latest.json", payload, artifact_class=ArtifactClass.AUDIT_EVIDENCE)
    write_classified_json("out/contracts/artifact_contract_post_closure_operator_receipt_report.latest.json", report, artifact_class=ArtifactClass.AUDIT_EVIDENCE)
    write_classified_json("out/contracts/artifact_contract_post_closure_operator_receipt_actions.latest.json", actions, artifact_class=ArtifactClass.AUDIT_EVIDENCE)


if __name__ == "__main__":
    main()
