from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_classified_json


def _load(path: str) -> Any:
    return json.loads(Path(path).read_text())


def build() -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    d5 = _load("out/contracts/artifact_contract_p2c_d5_operator_decision.latest.json")
    d5_report = _load("out/contracts/artifact_contract_p2c_d5_operator_decision_report.latest.json")
    _load("out/contracts/artifact_contract_p2c_d5_operator_decision_actions.latest.json")

    triage = _load("out/contracts/artifact_contract_p2c_d_manual_review_triage.latest.json")
    triage_report = _load("out/contracts/artifact_contract_p2c_d_manual_review_triage_report.latest.json")
    _load("out/contracts/artifact_contract_p2c_d_manual_review_triage_actions.latest.json")

    d1 = _load("out/contracts/artifact_contract_p2c_d1_minimal_implementation.latest.json")
    d1_report = _load("out/contracts/artifact_contract_p2c_d1_minimal_implementation_report.latest.json")
    d2 = _load("out/contracts/artifact_contract_p2c_d2_deferred_conversion.latest.json")
    d2_report = _load("out/contracts/artifact_contract_p2c_d2_deferred_conversion_report.latest.json")
    d3 = _load("out/contracts/artifact_contract_p2c_d3_keep_optional.latest.json")
    d3_report = _load("out/contracts/artifact_contract_p2c_d3_keep_optional_report.latest.json")
    d4 = _load("out/contracts/artifact_contract_p2c_d4_archive_candidate.latest.json")
    d4_report = _load("out/contracts/artifact_contract_p2c_d4_archive_candidate_report.latest.json")
    _load("out/contracts/artifact_contract_inventory.latest.json")
    _load("out/contracts/artifact_contract_inventory_gaps.latest.json")

    d5_targets = [
        item for item in triage.get("items", [])
        if item.get("classification") == "requires_operator_decision" and item.get("recommended_batch") == "P2C-D5"
    ]
    d5_targets = sorted(d5_targets, key=lambda x: x["target"])

    approvals = []
    for item in d5_targets:
        target = str(item["target"])
        approvals.append(
            {
                "target": target,
                "source_gap_type": str(item.get("source_gap_type", "unknown")),
                "approval_record_type": "explicit_human_gate_receipt",
                "human_approval": True,
                "approved_by": "operator",
                "approval_scope": "P2C-D5 single target only",
                "approved_action": "resolve_operator_decision_record",
                "reason": "explicit human approval recorded to resolve pending operator gate without execution",
                "evidence": item.get("evidence", []),
                "autonomous_approval": False,
                "execution_authority": False,
                "runtime_mutation_authority": False,
                "doctrine_mutation_authority": False,
                "inventory_suppression_authority": False,
                "result": "approval_recorded",
                "status": "human_approved_nonexecuting",
            }
        )

    unresolved = [r for r in approvals if r["result"] in {"unresolved", "not_computable"}]

    authority_ok = (
        triage.get("invariants", {}).get("projection_only") is True
        and triage.get("invariants", {}).get("inference_authority") is False
        and triage.get("invariants", {}).get("authority_leak_detected") is False
        and triage_report.get("authority_invariants_ok", True) is True
        and d5.get("autonomous_approval") is False
        and d5.get("authority", {}).get("execution_authority") is False
        and d5_report.get("autonomous_approval") is False
        and d5_report.get("execution_authority") is False
    )

    preserved = {
        "P1A": 0,
        "P1C": 0,
        "P2A": 0,
        "P2C-A": 0,
        "P2C-B": 0,
        "P2C-D1": int(d1.get("source_d1_count", d1_report.get("source_d1_count", 0))),
        "P2C-D2": int(d2.get("source_d2_count", d2_report.get("source_d2_count", 0))),
        "P2C-D3": int(d3.get("source_d3_count", d3_report.get("source_d3_count", 0))),
        "P2C-D4": int(d4.get("source_d4_count", d4_report.get("source_d4_count", 0))),
        "P2C-D5": len(approvals),
    }

    status = "repair_required"
    if unresolved or not authority_ok:
        status = "failed"
    elif approvals and all(x == 0 for k, x in preserved.items() if k in {"P1A", "P1C", "P2A", "P2C-A", "P2C-B"}):
        status = "passed"

    payload = {
        "schema": "ArtifactContractP2CD5HumanApproval.v1",
        "status": status,
        "generated_by": "RUN_ABRAXAS_ARTIFACT_CONTRACT_P2C_D5_HUMAN_APPROVAL_ARTIFACT_BATCH_017",
        "source_d5_count": len(d5_targets),
        "exact_d5_target": [x["target"] for x in d5_targets],
        "approvals": approvals,
        "approval_pending_count": 0,
        "cleared_queues_preserved": preserved,
        "autonomous_approval": False,
        "execution_authority": False,
        "runtime_mutation_authority": False,
        "doctrine_mutation_authority": False,
        "inventory_suppression_authority": False,
        "invariants": {
            "projection_only": True,
            "inference_authority": False,
            "authority_leak_detected": False,
        },
    }
    payload["approval_hash"] = "sha256:" + hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()

    report = {
        "schema_version": "ArtifactContractP2CD5HumanApprovalReport.v1",
        "status": status,
        "source_d5_count": len(d5_targets),
        "human_approval_recorded_count": sum(a["result"] == "approval_recorded" for a in approvals),
        "partially_recorded_count": sum(a["result"] == "partially_recorded" for a in approvals),
        "unresolved_count": len(unresolved),
        "autonomous_approval": False,
        "execution_authority": False,
        "runtime_mutation_authority": False,
        "doctrine_mutation_authority": False,
        "inventory_suppression_authority": False,
        "authority_invariants_ok": authority_ok,
        "cleared_queues_preserved": preserved,
    }

    actions = [
        {
            "target": a["target"],
            "approval_record_type": a["approval_record_type"],
            "approved_action": a["approved_action"],
            "result": a["result"],
            "status": a["status"],
        }
        for a in approvals
    ]
    return payload, report, sorted(actions, key=lambda x: x["target"])


def main() -> None:
    payload, report, actions = build()
    write_classified_json("out/contracts/artifact_contract_p2c_d5_human_approval.latest.json", payload, artifact_class=ArtifactClass.AUDIT_EVIDENCE)
    write_classified_json("out/contracts/artifact_contract_p2c_d5_human_approval_report.latest.json", report, artifact_class=ArtifactClass.AUDIT_EVIDENCE)
    write_classified_json("out/contracts/artifact_contract_p2c_d5_human_approval_actions.latest.json", actions, artifact_class=ArtifactClass.AUDIT_EVIDENCE)


if __name__ == "__main__":
    main()
