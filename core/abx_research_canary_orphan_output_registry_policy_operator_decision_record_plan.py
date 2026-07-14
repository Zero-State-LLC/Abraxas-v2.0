from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "AbxResearchCanaryOrphanOutputRegistryPolicyOperatorDecisionRecordPlan.v1"
PLAN_ID = "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_OPERATOR_DECISION_RECORD_PLAN_001"
REQUEST_JSON_PATH = Path(
    "out/operator_review/abx_research_canary_orphan_output_registry_policy_operator_decision_request_001.latest.json"
)
POLICY_REVIEW_JSON_PATH = Path(
    "out/operator_review/abx_research_canary_orphan_output_registry_policy_review_001.latest.json"
)
PLAN_JSON_PATH = Path(
    "out/operator_review/abx_research_canary_orphan_output_registry_policy_operator_decision_record_plan_001.latest.json"
)
PLAN_MD_PATH = Path(
    "out/operator_review/abx_research_canary_orphan_output_registry_policy_operator_decision_record_plan_001.latest.md"
)
DECISION_RECORD_LANE = "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_OPERATOR_DECISION_RECORD_001"

DECISION_OPTIONS: tuple[str, ...] = (
    "MAINTAIN_EXCLUDE_FROM_CANONICAL_REPAIR",
    "AUTHORIZE_ORPHAN_REGISTRY_INCLUSION_SPEC",
    "AUTHORIZE_ORPHAN_ARCHIVE_PLAN",
    "HOLD",
)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_abx_research_canary_orphan_output_registry_policy_operator_decision_record_plan(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    request = _read_json(root / REQUEST_JSON_PATH)
    review = _read_json(root / POLICY_REVIEW_JSON_PATH)

    request_ready = (
        request.get("status")
        == "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_OPERATOR_DECISION_REQUEST_EMITTED"
        and request.get("downstream_status") == "READY_FOR_OPERATOR_DECISION_RECORD_PLAN"
    )
    review_ready = (
        review.get("status") == "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_REVIEW_HELD_FOR_OPERATOR"
        and review.get("orphan_count") == 10
    )
    plan_ready = request_ready and review_ready

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": PLAN_ID,
        "status": (
            "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_OPERATOR_DECISION_RECORD_PLAN_READY"
            if plan_ready
            else "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_OPERATOR_DECISION_RECORD_PLAN_BLOCKED"
        ),
        "decision_record_plan_id": PLAN_ID,
        "command": "BUILD_ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_OPERATOR_DECISION_RECORD_PLAN_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "registry_mutation_allowed": False,
        "registry_mutation_performed": False,
        "implementation_authorized": False,
        "safe_to_auto_continue": False,
        "operator_input_required": True,
        "decision_scope": str(request.get("decision_scope", NOT_COMPUTABLE)),
        "target_surface": str(request.get("target_surface", NOT_COMPUTABLE)),
        "target_review_id": str(request.get("target_review_id", NOT_COMPUTABLE)),
        "orphan_count": int(review.get("orphan_count", 0)),
        "recommended_default_decision": "MAINTAIN_EXCLUDE_FROM_CANONICAL_REPAIR",
        "recommended_next_action": (
            "collect explicit operator decision evidence; default path maintains orphan exclusion "
            "from canonical registry repair while preserving separate orphan registry governance"
            if plan_ready
            else "repair orphan policy decision request and policy review prerequisites"
        ),
        "recommended_next_lane": DECISION_RECORD_LANE if plan_ready else NOT_COMPUTABLE,
        "decision_options": list(DECISION_OPTIONS),
        "required_operator_identity_fields": [
            "operator_id",
            "operator_name",
            "operator_role",
            "decision_timestamp_utc",
        ],
        "required_decision_fields": [
            "selected_decision",
            "decision_rationale",
            "decision_scope_acknowledged",
            "per_orphan_disposition_acknowledged",
        ],
        "required_acknowledgement_fields": [
            "advisory_only_acknowledged",
            "non_authoritative_acknowledged",
            "execution_authority_denied_acknowledged",
            "p130_advisory_hold_preservation_acknowledged",
            "separate_orphan_registry_governance_acknowledged",
        ],
        "required_evidence_fields": [
            "reviewed_request_id",
            "reviewed_request_hash",
            "reviewed_policy_review_hash",
            "reviewed_orphan_count",
        ],
        "allowed_follow_on_actions_if_exclude_maintained": [
            "SEAL_ORPHAN_POLICY_GOVERNANCE",
            "MAINTAIN_ORPHAN_EXCLUSION",
        ],
        "allowed_follow_on_actions_if_inclusion_authorized": [
            "AUTHOR_ORPHAN_REGISTRY_INCLUSION_EXECUTION_SPEC",
            "SEPARATE_ORPHAN_REGISTRY_GOVERNANCE",
        ],
        "allowed_follow_on_actions_if_archive_authorized": [
            "AUTHOR_ORPHAN_ARCHIVE_PLAN",
            "SEPARATE_ORPHAN_REGISTRY_GOVERNANCE",
        ],
        "allowed_follow_on_actions_if_held": [
            "MAINTAIN_ORPHAN_POLICY_HOLD",
            "WAIT_FOR_EXPLICIT_OPERATOR_DECISION_EVIDENCE",
        ],
        "disallowed_follow_on_actions": list(request.get("blocked_actions", [])),
        "future_record_output_candidates": [
            "out/operator_review/abx_research_canary_orphan_output_registry_policy_operator_decision_record_001.latest.json",
            "out/operator_review/abx_research_canary_orphan_output_registry_policy_operator_decision_record_001.latest.md",
        ],
        "required_review_artifacts": [
            str(REQUEST_JSON_PATH),
            str(POLICY_REVIEW_JSON_PATH),
        ],
        "source_request_path": str(REQUEST_JSON_PATH),
        "source_request_id": str(request.get("request_id", NOT_COMPUTABLE)),
        "source_policy_review_path": str(POLICY_REVIEW_JSON_PATH),
        "source_hashes": {
            "operator_decision_request": str(request.get("request_hash", NOT_COMPUTABLE)),
            "orphan_policy_review": str(review.get("review_hash", NOT_COMPUTABLE)),
        },
    }
    return {**packet, "decision_record_plan_hash": canonical_hash(packet)}


def render_abx_research_canary_orphan_output_registry_policy_operator_decision_record_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Research Canary Orphan Output Registry Policy Operator Decision Record Plan 001",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `target_surface`: `{packet['target_surface']}`",
        f"- `recommended_default_decision`: `{packet['recommended_default_decision']}`",
        f"- `recommended_next_lane`: `{packet['recommended_next_lane']}`",
        "",
        "## Decision Options",
    ]
    for option in packet.get("decision_options", []):
        lines.append(f"- `{option}`")
    lines.extend(["", "## Required Review Artifacts"])
    for item in packet.get("required_review_artifacts", []):
        lines.append(f"- `{item}`")
    return lines


def write_abx_research_canary_orphan_output_registry_policy_operator_decision_record_plan(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_research_canary_orphan_output_registry_policy_operator_decision_record_plan(root)
    write_canonical_json(target_root / PLAN_JSON_PATH, packet)
    _write_markdown(
        target_root / PLAN_MD_PATH,
        render_abx_research_canary_orphan_output_registry_policy_operator_decision_record_plan_markdown(packet),
    )
    return packet
