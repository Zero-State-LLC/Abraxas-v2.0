from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import write_canonical_json


def _load(path: str) -> Any:
    return json.loads(Path(path).read_text())


def build() -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    approval = _load("out/contracts/artifact_contract_p2c_d5_human_approval.latest.json")
    report = _load("out/contracts/artifact_contract_p2c_d5_human_approval_report.latest.json")
    triage = _load("out/contracts/artifact_contract_p2c_d_manual_review_triage.latest.json")

    source = {
        "P2C-D1": triage["counts"]["implement_minimal_coverage"],
        "P2C-D2": triage["counts"]["convert_to_deferred"],
        "P2C-D3": triage["counts"]["convert_to_keep_optional"],
        "P2C-D4": triage["counts"]["convert_to_archive_candidate"],
        "P2C-D5": triage["counts"]["requires_operator_decision"],
    }
    current = approval.get("cleared_queues_preserved", {})
    authority_ok = bool(report.get("authority_invariants_ok"))
    status = "passed" if authority_ok and report.get("unresolved_count") == 0 else "failed"

    payload = {
        "schema": "ArtifactContractP2CD5ApprovalRepairReverify.v1",
        "generated_by": "RUN_ABRAXAS_ARTIFACT_CONTRACT_P2C_D5_APPROVAL_REPAIR_AND_REVERIFY_BATCH_018",
        "status": status,
        "source_d5_count": report.get("source_d5_count", 0),
        "exact_d5_target": approval.get("exact_d5_target", []),
        "human_approval_recorded_count": report.get("human_approval_recorded_count", 0),
        "partially_recorded_count": report.get("partially_recorded_count", 0),
        "unresolved_count": report.get("unresolved_count", 0),
        "autonomous_approval": report.get("autonomous_approval", False),
        "execution_authority": report.get("execution_authority", False),
        "runtime_mutation_authority": report.get("runtime_mutation_authority", False),
        "doctrine_mutation_authority": report.get("doctrine_mutation_authority", False),
        "inventory_suppression_authority": report.get("inventory_suppression_authority", False),
        "authority_invariants_ok": authority_ok,
        "queue_counts_source": "artifact_contract_p2c_d_manual_review_triage.latest.json",
        "current_queue_counts": current,
        "stale_expectations_removed": True,
        "pytest_result": "see external run",
        "ruff_result": "see external run",
        "pyright_result": "see external run",
        "full_matrix_result": "see external run",
        "working_tree_result": "see external run",
        "remaining_limitations": [],
    }
    payload["repair_hash"] = "sha256:" + hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()

    rep = {k: payload[k] for k in payload if k not in {"exact_d5_target", "remaining_limitations"}}
    acts = [{"target": t, "source_count": c, "current_count": current.get(t)} for t, c in source.items()]
    return payload, rep, acts


def main() -> None:
    payload, report, actions = build()
    write_canonical_json("out/contracts/artifact_contract_p2c_d5_approval_repair_reverify.latest.json", payload)
    write_canonical_json("out/contracts/artifact_contract_p2c_d5_approval_repair_reverify_report.latest.json", report)
    write_canonical_json("out/contracts/artifact_contract_p2c_d5_approval_repair_reverify_actions.latest.json", actions)


if __name__ == "__main__":
    main()
