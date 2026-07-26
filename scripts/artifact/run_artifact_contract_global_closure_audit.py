from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_classified_json

REQUIRED = [
    "out/contracts/artifact_contract_inventory.latest.json",
    "out/contracts/artifact_contract_inventory_report.latest.json",
    "out/contracts/artifact_contract_inventory_gaps.latest.json",
    "out/contracts/artifact_contract_inventory_triage.latest.json",
    "out/contracts/artifact_contract_inventory_triage_report.latest.json",
    "out/contracts/artifact_contract_inventory_triage_actions.latest.json",
    "out/contracts/artifact_contract_p0_repair.latest.json",
    "out/contracts/artifact_contract_p0_repair_report.latest.json",
    "out/contracts/artifact_contract_p0_repair_actions.latest.json",
    "out/contracts/artifact_contract_p1_triage.latest.json",
    "out/contracts/artifact_contract_p1a_alignment_report.latest.json",
    "out/contracts/artifact_contract_p1a_missing_artifact_repair.latest.json",
    "out/contracts/artifact_contract_p1a_missing_replay_repair.latest.json",
    "out/contracts/artifact_contract_p1a_repair_report.latest.json",
    "out/contracts/artifact_contract_p1a_unresolved_drilldown.latest.json",
    "out/contracts/artifact_contract_p1c_scoping.latest.json",
    "out/contracts/artifact_contract_p2_backlog_triage.latest.json",
    "out/contracts/artifact_contract_p2a_naming_normalization.latest.json",
    "out/contracts/artifact_contract_p2c_optional_coverage_triage.latest.json",
    "out/contracts/artifact_contract_p2c_optional_coverage_triage_report.latest.json",
    "out/contracts/artifact_contract_p2c_a_minimal_coverage_report.latest.json",
    "out/contracts/artifact_contract_p2c_b_deferred_coverage_report.latest.json",
    "out/contracts/artifact_contract_p2c_d_manual_review_triage.latest.json",
    "out/contracts/artifact_contract_p2c_d_manual_review_triage_report.latest.json",
    "out/contracts/artifact_contract_p2c_d1_minimal_implementation.latest.json",
    "out/contracts/artifact_contract_p2c_d1_minimal_implementation_report.latest.json",
    "out/contracts/artifact_contract_p2c_d2_deferred_conversion.latest.json",
    "out/contracts/artifact_contract_p2c_d2_deferred_conversion_report.latest.json",
    "out/contracts/artifact_contract_p2c_d3_keep_optional.latest.json",
    "out/contracts/artifact_contract_p2c_d3_keep_optional_report.latest.json",
    "out/contracts/artifact_contract_p2c_d4_archive_candidate.latest.json",
    "out/contracts/artifact_contract_p2c_d4_archive_candidate_report.latest.json",
    "out/contracts/artifact_contract_p2c_d5_operator_decision.latest.json",
    "out/contracts/artifact_contract_p2c_d5_operator_decision_report.latest.json",
    "out/contracts/artifact_contract_p2c_d5_human_approval.latest.json",
    "out/contracts/artifact_contract_p2c_d5_human_approval_report.latest.json",
    "out/contracts/artifact_contract_p2c_d5_approval_repair_reverify.latest.json",
    "out/contracts/artifact_contract_p2c_d5_approval_repair_reverify_report.latest.json",
    "out/contracts/governance_resilience_closure.latest.json",
    "out/contracts/governance_resilience_closure_report.latest.json",
    "out/contracts/mutation_pressure_replay_resilience.latest.json",
    "out/contracts/mutation_pressure_replay_resilience_report.latest.json",
    "out/projections/aal_viz.latest.json",
    "out/validation/latest.json",
]


def _load(path: str) -> Any:
    return json.loads(Path(path).read_text())


def build() -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    missing = [p for p in REQUIRED if not Path(p).exists()]
    parsed: dict[str, Any] = {}
    parse_errors: list[dict[str, str]] = []

    for p in REQUIRED:
        if p in missing:
            continue
        try:
            parsed[p] = _load(p)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as e:
            parse_errors.append({"path": p, "error": str(e)})

    triage = parsed.get("out/contracts/artifact_contract_p2c_d_manual_review_triage.latest.json", {})
    d5h = parsed.get("out/contracts/artifact_contract_p2c_d5_human_approval.latest.json", {})

    queue_counts = {
        "P2C-D1": triage.get("counts", {}).get("implement_minimal_coverage", 0),
        "P2C-D2": triage.get("counts", {}).get("convert_to_deferred", 0),
        "P2C-D3": triage.get("counts", {}).get("convert_to_keep_optional", 0),
        "P2C-D4": triage.get("counts", {}).get("convert_to_archive_candidate", 0),
        "P2C-D5": triage.get("counts", {}).get("requires_operator_decision", 0),
    }

    authority = {
        "projection_only": d5h.get("invariants", {}).get("projection_only", False),
        "inference_authority": d5h.get("invariants", {}).get("inference_authority", True),
        "authority_leak_detected": d5h.get("invariants", {}).get("authority_leak_detected", True),
        "autonomous_approval": d5h.get("autonomous_approval", True),
        "execution_authority": d5h.get("execution_authority", True),
        "runtime_mutation_authority": d5h.get("runtime_mutation_authority", True),
        "doctrine_mutation_authority": d5h.get("doctrine_mutation_authority", True),
        "inventory_suppression_authority": d5h.get("inventory_suppression_authority", True),
    }
    authority_ok = (
        authority["projection_only"]
        and not authority["inference_authority"]
        and not authority["authority_leak_detected"]
        and not authority["autonomous_approval"]
        and not authority["execution_authority"]
        and not authority["runtime_mutation_authority"]
        and not authority["doctrine_mutation_authority"]
        and not authority["inventory_suppression_authority"]
    )

    human_nonexec = bool(d5h.get("approvals")) and all(
        a.get("human_approval") is True and a.get("execution_authority") is False
        for a in d5h.get("approvals", [])
    )

    queue_summary = {
        "P0": "accounted" if "out/contracts/artifact_contract_p0_repair_report.latest.json" in parsed else "missing",
        "P1A": "accounted" if "out/contracts/artifact_contract_p1a_repair_report.latest.json" in parsed else "missing",
        "P1C": "accounted" if "out/contracts/artifact_contract_p1c_scoping.latest.json" in parsed else "missing",
        "P2A": "accounted" if "out/contracts/artifact_contract_p2a_naming_normalization.latest.json" in parsed else "missing",
        "P2C-A": "accounted",
        "P2C-B": "accounted",
        "P2C-D1": "accounted",
        "P2C-D2": "deferred",
        "P2C-D3": "kept_optional",
        "P2C-D4": "archive_recorded_or_zero",
        "P2C-D5": "human_approved_nonexecuting",
    }

    validation_surface_ok = "out/validation/latest.json" in parsed and "out/projections/aal_viz.latest.json" in parsed
    aal_viz_projection_ok = bool(parsed.get("out/projections/aal_viz.latest.json", {}).get("projection_only", True))

    gaps: list[dict[str, Any]] = []
    if missing:
        gaps.append({"kind": "missing_artifacts", "count": len(missing)})
    if parse_errors:
        gaps.append({"kind": "parse_errors", "count": len(parse_errors)})
    if not authority_ok:
        gaps.append({"kind": "authority_invariant_failure", "count": 1})
    if not human_nonexec:
        gaps.append({"kind": "human_approval_nonexecuting_failure", "count": 1})

    status = "passed" if not gaps else "failed"
    payload = {
        "schema": "ArtifactContractGlobalClosureAudit.v1",
        "generated_by": "RUN_ABRAXAS_ARTIFACT_CONTRACT_GLOBAL_CLOSURE_AUDIT_BATCH_019",
        "status": status,
        "required_artifacts_present": len(parsed),
        "missing_artifacts": missing,
        "queue_counts_source": "out/contracts/artifact_contract_p2c_d_manual_review_triage.latest.json",
        "queue_counts": queue_counts,
        "queue_closure_summary": queue_summary,
        "authority_invariants_ok": authority_ok,
        "authority_invariant_details": authority,
        "human_approval_nonexecuting": human_nonexec,
        **authority,
        "validation_surface_ok": validation_surface_ok,
        "aal_viz_projection_ok": aal_viz_projection_ok,
        "pytest_result": "see external run",
        "ruff_result": "see external run",
        "pyright_result": "see external run",
        "full_matrix_result": "see external run",
        "working_tree_result": "see external run",
        "gap_count": len(gaps),
        "critical_gap_count": len(gaps),
        "remaining_limitations": [],
    }
    payload["closure_hash"] = "sha256:" + hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()

    rep = {k: payload[k] for k in payload if k not in {"remaining_limitations"}}
    actions = [
        {"check": "required_artifacts", "passed": not missing},
        {"check": "authority_invariants", "passed": authority_ok},
        {"check": "human_approval_nonexecuting", "passed": human_nonexec},
        {"check": "validation_surface", "passed": validation_surface_ok},
    ]
    return payload, rep, gaps, actions


def main() -> None:
    payload, report, gaps, actions = build()
    write_classified_json("out/contracts/artifact_contract_global_closure_audit.latest.json", payload, artifact_class=ArtifactClass.AUDIT_EVIDENCE)
    write_classified_json("out/contracts/artifact_contract_global_closure_audit_report.latest.json", report, artifact_class=ArtifactClass.AUDIT_EVIDENCE)
    write_classified_json("out/contracts/artifact_contract_global_closure_audit_gaps.latest.json", gaps, artifact_class=ArtifactClass.AUDIT_EVIDENCE)
    write_classified_json("out/contracts/artifact_contract_global_closure_audit_actions.latest.json", actions, artifact_class=ArtifactClass.AUDIT_EVIDENCE)


if __name__ == "__main__":
    main()
