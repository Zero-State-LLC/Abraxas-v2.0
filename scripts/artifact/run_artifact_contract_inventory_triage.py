from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import write_canonical_json

SOURCE_INVENTORY = "out/contracts/artifact_contract_inventory.latest.json"
SOURCE_REPORT = "out/contracts/artifact_contract_inventory_report.latest.json"
SOURCE_GAPS = "out/contracts/artifact_contract_inventory_gaps.latest.json"


def _load_json(path: str) -> Any:
    p = Path(path)
    if not p.exists():
        return None
    return json.loads(p.read_text())


def _gap_list(gaps_payload: Any) -> list[dict[str, Any]]:
    if isinstance(gaps_payload, list):
        return gaps_payload
    if isinstance(gaps_payload, dict) and isinstance(gaps_payload.get("gaps"), list):
        return gaps_payload["gaps"]
    return []


def classify_gap(gap: dict[str, Any]) -> dict[str, Any]:
    gap_type = str(gap.get("gap_type", "unknown"))
    subject = str(gap.get("subject", "unknown"))
    severity = str(gap.get("severity", "warning"))
    details = str(gap.get("details", ""))

    classification = "true_defect"
    confidence = "medium"
    priority = "P1" if severity == "critical" else "P3"
    action = "repair missing contract binding"

    naming_tokens = ["brier", "drift", "external_action_proposal", "governance_resilience_closure"]
    if any(t in subject for t in naming_tokens):
        classification = "naming_normalization_issue"
        confidence = "high"
        priority = "P2"
        action = "normalize producer/runtime naming map in inventory engine"
    elif gap_type in {"missing_test", "orphan_summary"}:
        classification = "audit_engine_rule_too_strict"
        confidence = "medium"
        priority = "P2"
        action = "scope test/summary requirements by subsystem category"
    elif "legacy" in subject or "legacy" in details:
        classification = "legacy_exception"
        confidence = "medium"
        priority = "defer"
        action = "document legacy exception without runtime mutation"
    elif gap_type == "duplicate_contract":
        classification = "deferred_scope"
        confidence = "medium"
        priority = "defer"
        action = "defer duplicate cleanup outside current repair perimeter"
    elif gap_type in {"missing_gate", "orphan_gate"} and severity == "critical":
        classification = "true_defect"
        confidence = "high"
        priority = "P0"
        action = "bind doctrine gate to active runtime contract"

    return {
        "gap_type": gap_type,
        "subject": subject,
        "source_severity": severity,
        "classification": classification,
        "confidence": confidence,
        "evidence": [details, str(gap.get("recommended_action", ""))],
        "recommended_action": action,
        "repair_priority": priority,
    }


def _status_from_counts(counts: dict[str, int]) -> str:
    if counts.get("p0", 0) > 0 and counts.get("true_defects", 0) > 0:
        return "failed"
    if counts.get("true_defects", 0) > 0 or counts.get("naming_normalization_issues", 0) > 0 or counts.get("audit_engine_rule_too_strict", 0) > 0:
        return "repair_required"
    if counts.get("legacy_exceptions", 0) > 0 or counts.get("false_positives", 0) > 0 or counts.get("deferred_scope", 0) > 0:
        return "passed_with_documented_exceptions"
    return "passed"


def build_triage_payload() -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    inventory = _load_json(SOURCE_INVENTORY)
    report = _load_json(SOURCE_REPORT)
    gaps_raw = _load_json(SOURCE_GAPS)
    if not isinstance(inventory, dict) or not isinstance(report, dict):
        triage = {
            "schema": "ArtifactContractInventoryTriage.v1",
            "status": "not_computable",
            "generated_by": "RUN_ABRAXAS_ARTIFACT_CONTRACT_INVENTORY_REPAIR_TRIAGE_001",
            "source_inventory_status": "not_computable",
            "source_gap_count": 0,
            "classifications": [],
            "counts": {
                "source_gaps": 0, "true_defects": 0, "legacy_exceptions": 0, "naming_normalization_issues": 0,
                "false_positives": 0, "audit_engine_rule_too_strict": 0, "deferred_scope": 0,
                "p0": 0, "p1": 0, "p2": 0, "p3": 0, "defer": 0,
            },
            "repair_plan": [],
            "authority": {"projection_only": True, "inference_authority": False, "mutation_authority": False, "execution_authority": False},
        }
        triage_hash = hashlib.sha256(json.dumps(triage, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        triage["triage_hash"] = f"sha256:{triage_hash}"
        report_payload = {"schema_version": "ArtifactContractInventoryTriageReport.v1", "status": "not_computable", "source_gap_count": 0, "classification_count": 0}
        return triage, report_payload, []

    source_gaps = sorted(_gap_list(gaps_raw), key=lambda g: (str(g.get("gap_type", "")), str(g.get("subject", ""))))
    classifications = [classify_gap(g) for g in source_gaps]

    counts = {
        "source_gaps": len(source_gaps),
        "true_defects": sum(c["classification"] == "true_defect" for c in classifications),
        "legacy_exceptions": sum(c["classification"] == "legacy_exception" for c in classifications),
        "naming_normalization_issues": sum(c["classification"] == "naming_normalization_issue" for c in classifications),
        "false_positives": sum(c["classification"] == "false_positive" for c in classifications),
        "audit_engine_rule_too_strict": sum(c["classification"] == "audit_engine_rule_too_strict" for c in classifications),
        "deferred_scope": sum(c["classification"] == "deferred_scope" for c in classifications),
        "p0": sum(c["repair_priority"] == "P0" for c in classifications),
        "p1": sum(c["repair_priority"] == "P1" for c in classifications),
        "p2": sum(c["repair_priority"] == "P2" for c in classifications),
        "p3": sum(c["repair_priority"] == "P3" for c in classifications),
        "defer": sum(c["repair_priority"] == "defer" for c in classifications),
    }

    status = _status_from_counts(counts)
    repair_plan = [
        {
            "priority": "P0",
            "target": "critical_gate_binding",
            "action": "bind missing/orphan critical gates to active runtime artifacts",
            "allowed_files": ["scripts/artifact/run_artifact_contract_inventory.py", "core/audit_artifact_contract_inventory.py", "tests/"],
            "forbidden_files": ["core/projections/aal_viz.py", "scripts/run_doctrine_validator.py"],
            "expected_test": "uv run pytest -q tests/test_artifact_contract_inventory*.py",
        },
        {
            "priority": "P2",
            "target": "naming_normalization_map",
            "action": "introduce deterministic alias map for known naming divergences",
            "allowed_files": ["core/audit_artifact_contract_inventory.py", "tests/"],
            "forbidden_files": ["core/projections/aal_viz.py", "core/pipelines/validator.py"],
            "expected_test": "uv run pytest -q tests/test_artifact_contract_inventory*.py",
        },
    ] if counts["source_gaps"] else []

    triage = {
        "schema": "ArtifactContractInventoryTriage.v1",
        "status": status,
        "generated_by": "RUN_ABRAXAS_ARTIFACT_CONTRACT_INVENTORY_REPAIR_TRIAGE_001",
        "source_inventory_status": report.get("status", "not_computable"),
        "source_gap_count": len(source_gaps),
        "classifications": classifications,
        "counts": counts,
        "repair_plan": sorted(repair_plan, key=lambda x: x["priority"]),
        "authority": {
            "projection_only": True,
            "inference_authority": False,
            "mutation_authority": False,
            "execution_authority": False,
        },
    }
    triage_hash = hashlib.sha256(json.dumps(triage, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    triage["triage_hash"] = f"sha256:{triage_hash}"
    report_payload = {
        "schema_version": "ArtifactContractInventoryTriageReport.v1",
        "status": status,
        "source_gap_count": len(source_gaps),
        "classification_count": len(classifications),
        "p0": counts["p0"],
        "p1": counts["p1"],
        "p2": counts["p2"],
        "p3": counts["p3"],
        "defer": counts["defer"],
    }
    actions = [
        {
            "priority": c["repair_priority"],
            "subject": c["subject"],
            "classification": c["classification"],
            "recommended_action": c["recommended_action"],
        }
        for c in classifications
    ]
    return triage, report_payload, sorted(actions, key=lambda x: (x["priority"], x["subject"]))


def main() -> None:
    triage, report, actions = build_triage_payload()
    write_canonical_json("out/contracts/artifact_contract_inventory_triage.latest.json", triage)
    write_canonical_json("out/contracts/artifact_contract_inventory_triage_report.latest.json", report)
    write_canonical_json("out/contracts/artifact_contract_inventory_triage_actions.latest.json", actions)


if __name__ == "__main__":
    main()
