from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "AbxArtifactLineageRunnerCasingPolicyReviewRequest.v1"
TRACEABILITY_AUDIT_PATH = Path("out/sync/abx_artifact_lineage_registry_traceability_audit/latest.json")
JSON_PATH = Path("out/operator_review/abx_artifact_lineage_runner_casing_policy_review_request_001.latest.json")
MD_PATH = Path("out/operator_review/abx_artifact_lineage_runner_casing_policy_review_request_001.latest.md")

BLOCKED_ACTIONS = [
    "RUNNER_CASING_POLICY_OVERRIDE",
    "RUNNER_PATH_NORMALIZATION",
    "SCRIPT_DISCOVERY_SEMANTICS_CHANGE",
    "CANON_MUTATION",
    "RUNTIME_MUTATION",
    "QUEUE_MUTATION",
    "SCHEDULER_MUTATION",
]

DECISION_OPTIONS = [
    "KEEP_CASE_SENSITIVE_RUNNER_DISCOVERY",
    "AUTHORIZE_CASE_INSENSITIVE_RUNNER_EQUIVALENCE_POLICY",
    "AUTHORIZE_REPO_WIDE_RUNNER_PATH_NORMALIZATION_PLAN",
    "REQUEST_ADDITIONAL_RUNNER_CASE_EVIDENCE",
]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _runner_casing_finding(audit: Mapping[str, Any]) -> dict[str, Any]:
    for finding in audit.get("runner_findings", []):
        if finding.get("finding_id") == "detect_uppercase_Scripts_runner_discovery_gaps":
            return dict(finding)
    return {
        "finding_id": "detect_uppercase_Scripts_runner_discovery_gaps",
        "status": "NOT_COMPUTABLE",
        "checked_count": 0,
        "impacted_count": 0,
        "sample_impacted": [],
        "reason": "runner casing policy requires explicit operator review",
        "evidence_required": "operator policy decision for uppercase Scripts runner discovery semantics",
    }


def build_abx_artifact_lineage_runner_casing_policy_review_request(source_root: str | Path = ".") -> dict[str, Any]:
    root = Path(source_root)
    audit = _read_json(root / TRACEABILITY_AUDIT_PATH)
    finding = _runner_casing_finding(audit)
    sample_impacted = sorted(str(item) for item in finding.get("sample_impacted", []))
    impacted_count = int(finding.get("impacted_count", len(sample_impacted)))
    source_audit_ready = (
        audit.get("artifact_type") == "AbxArtifactLineageRegistryTraceabilityAudit.v1"
        and finding.get("status") == "NOT_COMPUTABLE"
        and impacted_count > 0
    )

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": "ABX_ARTIFACT_LINEAGE_RUNNER_CASING_POLICY_REVIEW_REQUEST_HELD"
        if source_audit_ready
        else "ABX_ARTIFACT_LINEAGE_RUNNER_CASING_POLICY_REVIEW_REQUEST_BLOCKED",
        "artifact_id": "ABX_ARTIFACT_LINEAGE_RUNNER_CASING_POLICY_REVIEW_REQUEST_001",
        "request_hash": "",
        "command": "BUILD_ABX_ARTIFACT_LINEAGE_RUNNER_CASING_POLICY_REVIEW_REQUEST_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "policy_review_request_only": True,
        "source_traceability_audit": {
            "path": str(TRACEABILITY_AUDIT_PATH),
            "packet_hash": str(audit.get("packet_hash", "NOT_COMPUTABLE")),
            "audit_id": str(audit.get("audit_id", "NOT_COMPUTABLE")),
            "source_audit_ready": source_audit_ready,
        },
        "review_scope": "RUNNER_CASING_POLICY_DECISION_ONLY",
        "target_finding_id": str(finding.get("finding_id", "detect_uppercase_Scripts_runner_discovery_gaps")),
        "target_status": str(finding.get("status", "NOT_COMPUTABLE")),
        "impacted_runner_count": impacted_count,
        "sample_impacted_runners": sample_impacted,
        "required_evidence": str(
            finding.get("evidence_required", "operator policy decision for uppercase Scripts runner discovery semantics")
        ),
        "decision_question": (
            "Should repo-local artifact-lineage runner discovery treat uppercase Scripts runner paths as equivalent, "
            "or should a separate governed normalization plan be authored?"
        ),
        "decision_options": list(DECISION_OPTIONS),
        "recommended_decision": "REQUEST_ADDITIONAL_RUNNER_CASE_EVIDENCE",
        "runner_casing_policy_override_allowed": False,
        "runner_path_normalization_allowed": False,
        "script_discovery_semantics_change_allowed": False,
        "execution_authority": False,
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "scheduler_mutation_allowed": False,
        "valid_for_execution": False,
        "valid_for_repair": False,
        "safe_to_auto_continue": False,
        "safe_to_prepare_normalization_pr": False,
        "blocked_actions": list(BLOCKED_ACTIONS),
        "acceptance_gates": [
            {
                "gate_id": "operator_runner_casing_policy_decision_required",
                "status": "PENDING_OPERATOR_DECISION",
                "required_before": "any runner casing equivalence or normalization claim",
            },
            {
                "gate_id": "runner_mutation_denied",
                "status": "DENIED",
                "required_before": "any repo-local runner path mutation",
            },
            {
                "gate_id": "traceability_audit_replay_required",
                "status": "PENDING_AFTER_POLICY_DECISION",
                "required_before": "clearing the runner casing NOT_COMPUTABLE finding",
            },
        ],
        "recommended_next_action": (
            "collect an explicit operator policy decision for uppercase Scripts runner discovery semantics before "
            "any runner casing equivalence, normalization, or traceability-audit clearing claim"
        ),
        "recommended_next_lane": "ABX_ARTIFACT_LINEAGE_RUNNER_CASING_POLICY_DECISION_PLAN",
        "downstream_status": "HELD_FOR_OPERATOR_POLICY_DECISION",
    }
    packet["request_hash"] = canonical_hash({key: value for key, value in packet.items() if key != "request_hash"})
    return packet


def render_abx_artifact_lineage_runner_casing_policy_review_request_markdown(packet: Mapping[str, Any]) -> list[str]:
    lines = [
        "# ABX Artifact Lineage Runner Casing Policy Review Request",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `artifact_id`: `{packet['artifact_id']}`",
        f"- `review_scope`: `{packet['review_scope']}`",
        f"- `impacted_runner_count`: `{packet['impacted_runner_count']}`",
        f"- `runner_casing_policy_override_allowed`: `{packet['runner_casing_policy_override_allowed']}`",
        f"- `runner_path_normalization_allowed`: `{packet['runner_path_normalization_allowed']}`",
        f"- `execution_authority`: `{packet['execution_authority']}`",
        f"- `downstream_status`: `{packet['downstream_status']}`",
        f"- `recommended_next_lane`: `{packet['recommended_next_lane']}`",
        "",
        "## Decision Options",
        "",
    ]
    for item in packet["decision_options"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Sample Impacted Runners", ""])
    for item in packet["sample_impacted_runners"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Blocked Actions", ""])
    for item in packet["blocked_actions"]:
        lines.append(f"- `{item}`")
    return lines


def write_abx_artifact_lineage_runner_casing_policy_review_request(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_artifact_lineage_runner_casing_policy_review_request(root)
    write_canonical_json(target_root / JSON_PATH, packet)
    _write_markdown(
        target_root / MD_PATH,
        render_abx_artifact_lineage_runner_casing_policy_review_request_markdown(packet),
    )
    return packet
