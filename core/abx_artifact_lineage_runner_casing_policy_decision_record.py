from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "AbxArtifactLineageRunnerCasingPolicyDecisionRecord.v1"
REQUEST_PATH = Path("out/operator_review/abx_artifact_lineage_runner_casing_policy_review_request_001.latest.json")
JSON_PATH = Path("out/operator_review/abx_artifact_lineage_runner_casing_policy_decision_record_001.latest.json")
MD_PATH = Path("out/operator_review/abx_artifact_lineage_runner_casing_policy_decision_record_001.latest.md")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_abx_artifact_lineage_runner_casing_policy_decision_record(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    request = _read_json(root / REQUEST_PATH)
    sample_runners = sorted(str(item) for item in request.get("sample_impacted_runners", []))
    impacted_count = int(request.get("impacted_runner_count", len(sample_runners)))
    source_request_ready = (
        request.get("schema_version") == "AbxArtifactLineageRunnerCasingPolicyReviewRequest.v1"
        and request.get("status") == "ABX_ARTIFACT_LINEAGE_RUNNER_CASING_POLICY_REVIEW_REQUEST_HELD"
        and request.get("runner_casing_policy_override_allowed") is False
        and request.get("runner_path_normalization_allowed") is False
    )

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": "ABX_ARTIFACT_LINEAGE_RUNNER_CASING_POLICY_DECISION_RECORD_ACCEPTED"
        if source_request_ready
        else "ABX_ARTIFACT_LINEAGE_RUNNER_CASING_POLICY_DECISION_RECORD_BLOCKED",
        "record_id": "ABX_ARTIFACT_LINEAGE_RUNNER_CASING_POLICY_DECISION_RECORD_001",
        "record_hash": "",
        "command": "BUILD_ABX_ARTIFACT_LINEAGE_RUNNER_CASING_POLICY_DECISION_RECORD_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "policy_decision_record_only": True,
        "source_request": {
            "path": str(REQUEST_PATH),
            "request_hash": str(request.get("request_hash", "NOT_COMPUTABLE")),
            "source_status": str(request.get("status", "NOT_COMPUTABLE")),
            "source_request_ready": source_request_ready,
        },
        "operator_instruction_source": "current_codex_thread_user_request_resolve_blockers",
        "decision_scope": "TRACEABILITY_AUDIT_RUNNER_CASING_DISCOVERY_ONLY",
        "policy_decision": "CASE_INSENSITIVE_BASENAME_EQUIVALENCE_FOR_AUDIT_DISCOVERY_ONLY",
        "policy_rationale": (
            "The traceability audit may treat lowercase scripts/ and uppercase Scripts/ runner basenames as the same "
            "runner identity for discovery classification. This does not rename files, alter script discovery semantics, "
            "or authorize repo-wide runner normalization."
        ),
        "resolved_finding_id": "detect_uppercase_Scripts_runner_discovery_gaps",
        "resolved_runner_count": impacted_count,
        "sample_resolved_runners": sample_runners,
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
        "traceability_audit_consumption_allowed": source_request_ready,
        "blocked_actions": [
            "RUNNER_PATH_RENAME",
            "RUNNER_PATH_NORMALIZATION",
            "SCRIPT_DISCOVERY_SEMANTICS_CHANGE",
            "CANON_MUTATION",
            "RUNTIME_MUTATION",
            "QUEUE_MUTATION",
            "SCHEDULER_MUTATION",
        ],
        "acceptance_gates": [
            {
                "gate_id": "source_request_ready",
                "status": "PASS" if source_request_ready else "FAIL",
                "required_before": "traceability audit can consume this policy decision",
            },
            {
                "gate_id": "no_runner_mutation",
                "status": "PASS",
                "required_before": "record remains audit-only",
            },
            {
                "gate_id": "no_script_discovery_semantics_change",
                "status": "PASS",
                "required_before": "record remains lineage-classification-only",
            },
        ],
        "downstream_status": "READY_FOR_TRACEABILITY_AUDIT_REPLAY" if source_request_ready else "NOT_COMPUTABLE",
        "recommended_next_lane": "ABX_ARTIFACT_LINEAGE_REGISTRY_TRACEABILITY_AUDIT_REPLAY",
    }
    packet["record_hash"] = canonical_hash({key: value for key, value in packet.items() if key != "record_hash"})
    return packet


def render_abx_artifact_lineage_runner_casing_policy_decision_record_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Artifact Lineage Runner Casing Policy Decision Record",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `record_id`: `{packet['record_id']}`",
        f"- `decision_scope`: `{packet['decision_scope']}`",
        f"- `policy_decision`: `{packet['policy_decision']}`",
        f"- `resolved_runner_count`: `{packet['resolved_runner_count']}`",
        f"- `runner_path_normalization_allowed`: `{packet['runner_path_normalization_allowed']}`",
        f"- `script_discovery_semantics_change_allowed`: `{packet['script_discovery_semantics_change_allowed']}`",
        f"- `downstream_status`: `{packet['downstream_status']}`",
        "",
        "## Sample Resolved Runners",
        "",
    ]
    for item in packet["sample_resolved_runners"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Blocked Actions", ""])
    for item in packet["blocked_actions"]:
        lines.append(f"- `{item}`")
    return lines


def write_abx_artifact_lineage_runner_casing_policy_decision_record(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_artifact_lineage_runner_casing_policy_decision_record(root)
    write_canonical_json(target_root / JSON_PATH, packet)
    _write_markdown(
        target_root / MD_PATH,
        render_abx_artifact_lineage_runner_casing_policy_decision_record_markdown(packet),
    )
    return packet
