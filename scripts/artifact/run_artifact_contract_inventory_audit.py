from __future__ import annotations

import json
from pathlib import Path

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_classified_json

SUBSYSTEMS = [
    {
        "name": "external_action_proposals",
        "producer": "core/external_action_proposals/runtime.py",
        "runtime": "out/external_action_proposals/latest.json",
        "replay": "out/external_action_proposals_replay/latest.json",
        "lineage": "out/external_action_proposals_lineage/latest.json",
        "diagnostics": "out/external_action_proposals_diagnostics/latest.json",
        "validator": "core/external_action_proposals/validators.py",
        "summary": "external_action_proposal_summary",
        "test_patterns": ["test_external_action_*.py"],
        "gates": ["external_action_proposal_gate", "external_action_category_gate", "external_action_constraint_gate", "external_action_readiness_gate", "external_action_governance_gate", "external_action_replay_gate", "external_action_operator_review_gate"],
    },
    {
        "name": "proposal_sandbox_routing",
        "producer": "core/proposal_sandbox_routing/runtime.py",
        "runtime": "out/proposal_sandbox_routing/latest.json",
        "replay": "out/proposal_sandbox_routing_replay/latest.json",
        "lineage": "out/proposal_sandbox_routing_lineage/latest.json",
        "diagnostics": "out/proposal_sandbox_routing_diagnostics/latest.json",
        "validator": "core/proposal_sandbox_routing/validators.py",
        "summary": "proposal_sandbox_routing_summary",
        "test_patterns": ["test_proposal_sandbox_*.py"],
        "gates": ["proposal_sandbox_route_gate", "proposal_sandbox_lane_gate", "proposal_sandbox_constraint_gate", "proposal_sandbox_eligibility_gate", "proposal_sandbox_governance_gate", "proposal_sandbox_replay_gate", "proposal_sandbox_operator_review_gate"],
    },
    {
        "name": "proposal_sandbox_evaluation",
        "producer": "core/proposal_sandbox_evaluation/runtime.py",
        "runtime": "out/proposal_sandbox_evaluation/latest.json",
        "replay": "out/proposal_sandbox_evaluation_replay/latest.json",
        "lineage": "out/proposal_sandbox_evaluation_lineage/latest.json",
        "diagnostics": "out/proposal_sandbox_evaluation_diagnostics/latest.json",
        "validator": "core/proposal_sandbox_evaluation/validators.py",
        "summary": "proposal_sandbox_evaluation_summary",
        "test_patterns": ["test_proposal_sandbox_evaluation_*.py"],
        "gates": ["proposal_sandbox_evaluation_gate", "proposal_sandbox_score_gate", "proposal_sandbox_rationale_gate", "proposal_sandbox_restriction_gate", "proposal_sandbox_replay_gate", "proposal_sandbox_operator_review_gate"],
    },
    {
        "name": "proposal_decision_bridge",
        "producer": "core/proposal_decision_bridge/runtime.py",
        "runtime": "out/proposal_decision_bridge/latest.json",
        "replay": "out/proposal_decision_bridge_replay/latest.json",
        "lineage": "out/proposal_decision_bridge_lineage/latest.json",
        "diagnostics": "out/proposal_decision_bridge_diagnostics/latest.json",
        "validator": "core/proposal_decision_bridge/validators.py",
        "summary": "proposal_decision_bridge_summary",
        "test_patterns": ["test_proposal_decision_bridge_*.py"],
        "gates": ["proposal_decision_bridge_gate", "proposal_decision_input_gate", "proposal_decision_rationale_gate", "proposal_decision_restriction_gate", "proposal_decision_replay_gate", "proposal_decision_operator_review_gate"],
    },
    {
        "name": "human_decision_ledger",
        "producer": "core/human_decision_ledger/runtime.py",
        "runtime": "out/human_decision_ledger/latest.json",
        "replay": "out/human_decision_ledger_replay/latest.json",
        "lineage": "out/human_decision_ledger_lineage/latest.json",
        "diagnostics": "out/human_decision_ledger_diagnostics/latest.json",
        "validator": "core/human_decision_ledger/validators.py",
        "summary": "human_decision_ledger_summary",
        "test_patterns": ["test_human_decision_ledger_*.py"],
        "gates": ["human_decision_ledger_gate", "human_decision_rationale_gate", "human_decision_blocker_gate", "human_decision_deferral_gate", "human_decision_replay_gate", "human_decision_operator_review_gate"],
    },
    {
        "name": "human_decision_continuity",
        "producer": "core/human_decision_continuity/runtime.py",
        "runtime": "out/human_decision_continuity/latest.json",
        "replay": "out/human_decision_continuity_replay/latest.json",
        "lineage": "out/human_decision_continuity_lineage/latest.json",
        "diagnostics": "out/human_decision_continuity_diagnostics/latest.json",
        "validator": "core/human_decision_continuity/validators.py",
        "summary": "human_decision_continuity_summary",
        "test_patterns": ["test_human_decision_continuity_*.py"],
        "gates": ["human_decision_continuity_chain_gate", "human_decision_continuity_inheritance_gate", "human_decision_continuity_deferral_gate", "human_decision_continuity_blocker_gate", "human_decision_continuity_replay_gate", "human_decision_continuity_operator_review_gate"],
    },
]



def _load_json(path: str) -> dict | list | None:
    p = Path(path)
    if not p.exists():
        return None
    return json.loads(p.read_text())


def _schema_fields(payload: dict | list | None) -> list[str]:
    if isinstance(payload, dict):
        return sorted(payload.keys())
    if isinstance(payload, list):
        return ["list"]
    return []


def main() -> None:
    validation = _load_json("out/validation/latest.json") or {}
    projection = _load_json("out/projections/aal_viz.latest.json") or {}
    validation_text = json.dumps(validation, sort_keys=True)

    inventory = []
    gaps = []

    for subsystem in SUBSYSTEMS:
        runtime_payload = _load_json(subsystem["runtime"])
        replay_payload = _load_json(subsystem["replay"])
        lineage_payload = _load_json(subsystem["lineage"])
        diagnostics_payload = _load_json(subsystem["diagnostics"])

        tests = []
        for pattern in subsystem["test_patterns"]:
            tests.extend(Path("tests").glob(pattern))
        tests = sorted(set(tests))
        test_coverage_detected = bool(tests)

        required_missing = [
            key
            for key, payload in {
                "runtime": runtime_payload,
                "replay": replay_payload,
                "lineage": lineage_payload,
                "diagnostics": diagnostics_payload,
            }.items()
            if payload is None
        ]

        missing_gates = [g for g in subsystem["gates"] if g not in validation_text]
        summary_missing = subsystem["summary"] not in projection

        status = "passed"
        if required_missing:
            status = "failed"
        elif missing_gates or summary_missing or not test_coverage_detected:
            status = "repair_required"

        if missing_gates:
            gaps.append({"subsystem": subsystem["name"], "type": "missing_gates", "items": missing_gates})
        if summary_missing:
            gaps.append({"subsystem": subsystem["name"], "type": "missing_projection_summary", "items": [subsystem["summary"]]})
        if required_missing:
            gaps.append({"subsystem": subsystem["name"], "type": "missing_artifacts", "items": required_missing})
        if not test_coverage_detected:
            gaps.append({"subsystem": subsystem["name"], "type": "missing_tests", "items": []})

        inventory.append(
            {
                "subsystem": subsystem["name"],
                "producer_file": subsystem["producer"],
                "artifact_path": subsystem["runtime"],
                "artifact_type": "runtime",
                "schema_fields": _schema_fields(runtime_payload),
                "doctrine_gate_names": subsystem["gates"],
                "projection_summary_name": subsystem["summary"],
                "replay_surface": subsystem["replay"],
                "lineage_surface": subsystem["lineage"],
                "diagnostics_surface": subsystem["diagnostics"],
                "validator_surface": subsystem["validator"],
                "test_coverage_detected": test_coverage_detected,
                "status": status,
            }
        )

    projection_only = projection.get("projection_only") is True
    inference_authority = projection.get("inference_authority") is False
    invariant_ok = projection_only and inference_authority
    if not invariant_ok:
        gaps.append({"subsystem": "projection", "type": "invariant_violation", "items": ["projection_only/inference_authority"]})

    overall = "passed"
    if any(entry["status"] == "failed" for entry in inventory) or not invariant_ok:
        overall = "failed"
    elif gaps:
        overall = "repair_required"

    report = {
        "schema_version": "ArtifactContractInventoryReport.v1",
        "status": overall,
        "inventory_count": len(inventory),
        "gap_count": len(gaps),
        "projection_invariants": {
            "projection_only": projection.get("projection_only"),
            "inference_authority": projection.get("inference_authority"),
        },
        "authority_leak_detected": not invariant_ok,
    }

    write_classified_json("out/contracts/artifact_contract_inventory.latest.json", sorted(inventory, key=lambda x: x["subsystem"]), artifact_class=ArtifactClass.AUDIT_EVIDENCE)
    write_classified_json("out/contracts/artifact_contract_inventory_report.latest.json", report, artifact_class=ArtifactClass.AUDIT_EVIDENCE)
    write_classified_json("out/contracts/artifact_contract_inventory_gaps.latest.json", sorted(gaps, key=lambda x: (x["subsystem"], x["type"])), artifact_class=ArtifactClass.AUDIT_EVIDENCE)


if __name__ == "__main__":
    main()
