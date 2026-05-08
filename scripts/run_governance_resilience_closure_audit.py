from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import write_canonical_json

REQUIRED_GATES = sorted([
    "external_action_proposal_gate",
    "external_action_category_gate",
    "external_action_constraint_gate",
    "external_action_readiness_gate",
    "external_action_governance_gate",
    "external_action_replay_gate",
    "external_action_operator_review_gate",
    "proposal_sandbox_route_gate",
    "proposal_sandbox_lane_gate",
    "proposal_sandbox_constraint_gate",
    "proposal_sandbox_eligibility_gate",
    "proposal_sandbox_governance_gate",
    "proposal_sandbox_replay_gate",
    "proposal_sandbox_operator_review_gate",
    "proposal_sandbox_evaluation_gate",
    "proposal_sandbox_score_gate",
    "proposal_sandbox_rationale_gate",
    "proposal_sandbox_restriction_gate",
    "proposal_sandbox_replay_gate",
    "proposal_sandbox_operator_review_gate",
    "proposal_decision_bridge_gate",
    "proposal_decision_input_gate",
    "proposal_decision_rationale_gate",
    "proposal_decision_restriction_gate",
    "proposal_decision_replay_gate",
    "proposal_decision_operator_review_gate",
    "human_decision_ledger_gate",
    "human_decision_rationale_gate",
    "human_decision_blocker_gate",
    "human_decision_deferral_gate",
    "human_decision_replay_gate",
    "human_decision_operator_review_gate",
    "human_decision_continuity_chain_gate",
    "human_decision_continuity_inheritance_gate",
    "human_decision_continuity_deferral_gate",
    "human_decision_continuity_blocker_gate",
    "human_decision_continuity_replay_gate",
    "human_decision_continuity_operator_review_gate",
])

REQUIRED_SUMMARIES = sorted([
    "external_action_proposal_summary",
    "proposal_sandbox_routing_summary",
    "proposal_sandbox_evaluation_summary",
    "proposal_decision_bridge_summary",
    "human_decision_ledger_summary",
    "human_decision_continuity_summary",
])

SOURCE_CONFIG = [
    ("artifact_contract_inventory", "out/contracts/artifact_contract_inventory_report.latest.json", "out/contracts/artifact_contract_inventory_gaps.latest.json"),
    ("runtime_test_coverage_correlation", "out/contracts/runtime_test_coverage_correlation_report.latest.json", "out/contracts/runtime_test_coverage_correlation_gaps.latest.json"),
    ("mutation_pressure_replay_resilience", "out/contracts/mutation_pressure_replay_resilience_report.latest.json", "out/contracts/mutation_pressure_replay_resilience_gaps.latest.json"),
]


def _load_json(path: str) -> Any:
    p = Path(path)
    if not p.exists():
        return None
    return json.loads(p.read_text())


def _status_from_report(report: dict[str, Any]) -> str:
    value = report.get("status", "not_computable")
    if value in {"passed", "repair_required", "failed", "not_computable"}:
        return value
    return "not_computable"


def _build_source_audits() -> tuple[list[dict[str, Any]], list[dict[str, Any]], bool]:
    rows: list[dict[str, Any]] = []
    gaps: list[dict[str, Any]] = []
    readable = True
    for name, report_path, gap_path in sorted(SOURCE_CONFIG):
        report = _load_json(report_path)
        gap_payload = _load_json(gap_path)
        if not isinstance(report, dict) or not isinstance(gap_payload, list):
            readable = False
            continue
        status = _status_from_report(report)
        gap_count = int(report.get("gap_count", len(gap_payload)))
        critical_gap_count = gap_count if status in {"failed", "not_computable"} else 0
        rows.append(
            {
                "name": name,
                "status": status,
                "gap_count": gap_count,
                "critical_gap_count": critical_gap_count,
                "artifact_path": report_path,
            }
        )
        if gap_payload:
            gaps.append({"subsystem": name, "type": "source_audit_gaps", "items": sorted(str(x) for x in gap_payload)})
    return sorted(rows, key=lambda x: x["name"]), sorted(gaps, key=lambda x: x["subsystem"]), readable


def _extract_missing_gates(validation_payload: dict[str, Any]) -> list[str]:
    text = json.dumps(validation_payload, sort_keys=True)
    return sorted(g for g in REQUIRED_GATES if g not in text)


def _extract_missing_summaries(projection_payload: dict[str, Any]) -> list[str]:
    return sorted(s for s in REQUIRED_SUMMARIES if s not in projection_payload)


def _compute_status(
    *,
    source_audits: list[dict[str, Any]],
    mutation_gaps_empty: bool,
    projection_only: bool,
    inference_authority: bool,
    authority_leak_detected: bool,
    missing_gates: list[str],
    missing_summaries: list[str],
    readable: bool,
) -> str:
    if not readable:
        return "not_computable"
    statuses = {a["status"] for a in source_audits}
    any_failed = bool(statuses.intersection({"failed", "not_computable"}))
    any_repair_required = "repair_required" in statuses
    if any_failed or not mutation_gaps_empty or not projection_only or inference_authority or authority_leak_detected or missing_gates or missing_summaries:
        return "failed"
    if any_repair_required:
        return "repair_required"
    return "passed"


def build_closure_payload() -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    source_audits, source_gaps, readable = _build_source_audits()
    validation = _load_json("out/validation/latest.json")
    projection = _load_json("out/projections/aal_viz.latest.json")
    mutation_gaps = _load_json("out/contracts/mutation_pressure_replay_resilience_gaps.latest.json")
    if not isinstance(validation, dict) or not isinstance(projection, dict) or not isinstance(mutation_gaps, list):
        readable = False
        validation = validation if isinstance(validation, dict) else {}
        projection = projection if isinstance(projection, dict) else {}
        mutation_gaps = mutation_gaps if isinstance(mutation_gaps, list) else ["missing_required_artifact"]

    missing_gates = _extract_missing_gates(validation)
    missing_summaries = _extract_missing_summaries(projection)
    mutation_gaps_empty = len(mutation_gaps) == 0
    projection_only = projection.get("projection_only") is True
    inference_authority = projection.get("inference_authority") is True
    authority_leak_detected = projection.get("inference_authority") is not False

    cross_checks = {
        "contract_inventory_passed": any(a["name"] == "artifact_contract_inventory" and a["status"] == "passed" for a in source_audits),
        "coverage_correlation_passed": any(a["name"] == "runtime_test_coverage_correlation" and a["status"] == "passed" for a in source_audits),
        "mutation_resilience_passed": any(a["name"] == "mutation_pressure_replay_resilience" and a["status"] == "passed" for a in source_audits),
        "mutation_gaps_empty": mutation_gaps_empty,
        "doctrine_validation_present": bool(validation),
        "aal_viz_projection_present": bool(projection),
        "projection_only": projection_only,
        "inference_authority": projection.get("inference_authority"),
        "authority_leak_detected": authority_leak_detected,
    }

    gaps = source_gaps
    if missing_gates:
        gaps.append({"subsystem": "validation", "type": "missing_required_gates", "items": missing_gates})
    if missing_summaries:
        gaps.append({"subsystem": "projection", "type": "missing_required_summaries", "items": missing_summaries})
    if not mutation_gaps_empty:
        gaps.append({"subsystem": "mutation_pressure_replay_resilience", "type": "mutation_gaps_non_empty", "items": sorted(str(x) for x in mutation_gaps)})

    status = _compute_status(
        source_audits=source_audits,
        mutation_gaps_empty=mutation_gaps_empty,
        projection_only=projection_only,
        inference_authority=inference_authority,
        authority_leak_detected=authority_leak_detected,
        missing_gates=missing_gates,
        missing_summaries=missing_summaries,
        readable=readable,
    )

    closure = {
        "schema": "GovernanceResilienceClosure.v1",
        "status": status,
        "generated_by": "RUN_ABRAXAS_GOVERNANCE_RESILIENCE_CLOSURE_AUDIT_001",
        "source_audits": source_audits,
        "cross_checks": cross_checks,
        "required_gates_present": sorted(g for g in REQUIRED_GATES if g not in missing_gates),
        "required_summaries_present": sorted(s for s in REQUIRED_SUMMARIES if s not in missing_summaries),
        "gaps": sorted(gaps, key=lambda x: (x["subsystem"], x["type"])),
        "authority": {
            "projection_only": projection_only,
            "inference_authority": projection.get("inference_authority"),
            "mutation_authority": False,
            "execution_authority": False,
        },
    }
    hash_input = dict(closure)
    closure_hash = hashlib.sha256(json.dumps(hash_input, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    closure["closure_hash"] = f"sha256:{closure_hash}"

    report = {
        "schema_version": "GovernanceResilienceClosureReport.v1",
        "status": status,
        "source_audit_count": len(source_audits),
        "gap_count": len(closure["gaps"]),
        "critical_gap_count": sum(a["critical_gap_count"] for a in source_audits),
        "projection_only": projection_only,
        "inference_authority": projection.get("inference_authority"),
        "authority_leak_detected": authority_leak_detected,
    }
    return closure, report, closure["gaps"]


def main() -> None:
    closure, report, gaps = build_closure_payload()
    write_canonical_json("out/contracts/governance_resilience_closure.latest.json", closure)
    write_canonical_json("out/contracts/governance_resilience_closure_report.latest.json", report)
    write_canonical_json("out/contracts/governance_resilience_closure_gaps.latest.json", gaps)


if __name__ == "__main__":
    main()
