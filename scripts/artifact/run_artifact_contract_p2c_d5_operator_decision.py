from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import write_canonical_json


def _load(path: str) -> Any:
    return json.loads(Path(path).read_text())


def _decision_type(target: str, source_gap_type: str) -> str:
    if "operator" in target:
        return "operator_decision_required"
    if source_gap_type == "missing_test":
        return "manual_review_required"
    if source_gap_type in {"missing_producer", "missing_replay"}:
        return "optional_surface_policy_decision"
    if "governance" in target:
        return "governance_preference_required"
    return "deferred_operator_choice"


def build() -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    triage = _load("out/contracts/artifact_contract_p2c_d_manual_review_triage.latest.json")
    triage_report = _load("out/contracts/artifact_contract_p2c_d_manual_review_triage_report.latest.json")
    d4_report = _load("out/contracts/artifact_contract_p2c_d4_archive_candidate_report.latest.json")

    triage_report_invariants_ok = triage_report.get("authority_invariants_ok", True)

    d5_items = [
        item
        for item in triage.get("items", [])
        if item.get("classification") == "requires_operator_decision" and item.get("recommended_batch") == "P2C-D5"
    ]
    d5_items = sorted(d5_items, key=lambda x: x["target"])

    decisions = []
    for item in d5_items:
        target = str(item["target"])
        source_gap_type = str(item.get("source_gap_type", "unknown"))
        decisions.append(
            {
                "target": target,
                "source_gap_type": source_gap_type,
                "decision_record_type": _decision_type(target, source_gap_type),
                "reason": "operator decision required; no auto-approval or execution granted",
                "evidence": item.get("evidence", []),
                "operator_options": ["approve_keep_optional", "approve_deferred", "approve_archive", "request_retriage"],
                "recommended_default": "approve_keep_optional",
                "result": "decision_recorded",
                "status": "pending_operator_approval",
            }
        )

    unresolved = [r for r in decisions if r["result"] in {"unresolved", "not_computable"}]
    pending = sum(d["status"] == "pending_operator_approval" for d in decisions)

    invariants_ok = (
        triage.get("invariants", {}).get("projection_only") is True
        and triage.get("invariants", {}).get("inference_authority") is False
        and triage.get("invariants", {}).get("authority_leak_detected") is False
        and triage_report_invariants_ok is True
    )

    status = "repair_required"
    if unresolved or not invariants_ok:
        status = "failed"
    elif pending == 0 and decisions:
        status = "passed"

    payload = {
        "schema": "ArtifactContractP2CD5OperatorDecision.v1",
        "status": status,
        "generated_by": "RUN_ABRAXAS_ARTIFACT_CONTRACT_P2C_D5_OPERATOR_DECISION_BATCH_016",
        "source_d5_count": len(d5_items),
        "decisions": decisions,
        "operator_approval_pending_count": pending,
        "cleared_queues_preserved": {
            "P1A": 0,
            "P1C": 0,
            "P2A": 0,
            "P2C-A": 0,
            "P2C-B": 0,
            "P2C-D1": 5,
            "P2C-D2": 30,
            "P2C-D3": 6,
            "P2C-D4": int(d4_report.get("archive_candidate_recorded_count", 0)),
        },
        "autonomous_approval": False,
        "authority": {
            "projection_only": True,
            "inference_authority": False,
            "mutation_authority": False,
            "execution_authority": False,
        },
    }
    payload["decision_hash"] = "sha256:" + hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    report = {
        "schema_version": "ArtifactContractP2CD5OperatorDecisionReport.v1",
        "status": status,
        "source_d5_count": len(d5_items),
        "decision_recorded_count": sum(d["result"] == "decision_recorded" for d in decisions),
        "partially_recorded_count": sum(d["result"] == "partially_recorded" for d in decisions),
        "unresolved_count": len(unresolved),
        "operator_approval_pending_count": pending,
        "authority_invariants_ok": invariants_ok,
        "autonomous_approval": False,
        "execution_authority": False,
    }

    actions = [
        {
            "target": row["target"],
            "decision_record_type": row["decision_record_type"],
            "result": row["result"],
            "status": row["status"],
        }
        for row in decisions
    ]
    return payload, report, sorted(actions, key=lambda x: x["target"])


def main() -> None:
    payload, report, actions = build()
    write_canonical_json("out/contracts/artifact_contract_p2c_d5_operator_decision.latest.json", payload)
    write_canonical_json("out/contracts/artifact_contract_p2c_d5_operator_decision_report.latest.json", report)
    write_canonical_json("out/contracts/artifact_contract_p2c_d5_operator_decision_actions.latest.json", actions)


if __name__ == "__main__":
    main()
