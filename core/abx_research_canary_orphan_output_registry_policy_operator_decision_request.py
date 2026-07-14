from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_research_canary_orphan_output_registry_policy_review import (
    BLOCKED_ACTIONS as POLICY_REVIEW_BLOCKED_ACTIONS,
    POLICY_OPTIONS,
    REVIEW_ID,
)
from core.canonical.json import canonical_hash, write_canonical_json

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "AbxResearchCanaryOrphanOutputRegistryPolicyOperatorDecisionRequest.v1"
REQUEST_ID = "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_OPERATOR_DECISION_REQUEST_001"
POLICY_REVIEW_JSON_PATH = Path(
    "out/operator_review/abx_research_canary_orphan_output_registry_policy_review_001.latest.json"
)
OUT_JSON = Path(
    "out/operator_review/abx_research_canary_orphan_output_registry_policy_operator_decision_request_001.latest.json"
)
OUT_MD = Path(
    "out/operator_review/abx_research_canary_orphan_output_registry_policy_operator_decision_request_001.latest.md"
)
DECISION_RECORD_PLAN_LANE = (
    "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_OPERATOR_DECISION_RECORD_PLAN_001"
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


def _validate_policy_review(review: Mapping[str, Any]) -> bool:
    return (
        review.get("schema_version") == "AbxResearchCanaryOrphanOutputRegistryPolicyReview.v1"
        and review.get("artifact_id") == REVIEW_ID
        and review.get("status") == "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_REVIEW_HELD_FOR_OPERATOR"
        and review.get("policy_review_only") is True
        and review.get("registry_mutation_performed") is False
        and review.get("orphan_count") == 10
    )


def build_abx_research_canary_orphan_output_registry_policy_operator_decision_request(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    review = _read_json(root / POLICY_REVIEW_JSON_PATH)
    review_ready = _validate_policy_review(review)

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": REQUEST_ID,
        "status": (
            "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_OPERATOR_DECISION_REQUEST_EMITTED"
            if review_ready
            else "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_OPERATOR_DECISION_REQUEST_BLOCKED"
        ),
        "request_id": REQUEST_ID,
        "command": "BUILD_ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_OPERATOR_DECISION_REQUEST_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "evidence_only": True,
        "execution_authority": False,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "registry_mutation_allowed": False,
        "registry_mutation_performed": False,
        "implementation_authorized": False,
        "safe_to_auto_continue": False,
        "decision_scope": "ORPHAN_RESEARCH_OUTPUT_REGISTRY_POLICY_DECISION_REQUIRED",
        "decision_question": str(
            review.get(
                "decision_question",
                "Should orphan research outputs remain excluded from canonical P103-P130 registry repair?",
            )
        ),
        "target_surface": "ABX Research Canary Orphan Output Registry Policy",
        "target_review_id": REVIEW_ID,
        "orphan_count": int(review.get("orphan_count", 0)),
        "priority": "P0",
        "queue_action": "HOLD_FOR_GOVERNED_OPERATOR_DECISION",
        "decision_options": list(review.get("policy_options", POLICY_OPTIONS)),
        "recommended_decision": str(review.get("recommended_policy", "EXCLUDE_FROM_CANONICAL_REPAIR")),
        "recommended_next_action": (
            "review orphan policy options and collect explicit operator decision evidence before any "
            "orphan registry inclusion or archive lane"
            if review_ready
            else "complete orphan policy review prerequisites before operator decision request"
        ),
        "required_operator_actions": [
            "review_orphan_output_registry_policy_review",
            "review_per_orphan_disposition_options",
            "confirm_p130_advisory_hold_preservation",
            "confirm_separate_orphan_registry_governance",
            "collect_orphan_policy_operator_decision",
            "record_orphan_policy_operator_decision",
        ],
        "required_evidence": [
            "orphan_policy_review_ready",
            "explicit_operator_decision_record",
            "p130_hold_boundary_acknowledgement",
        ],
        "blocked_actions": [
            *POLICY_REVIEW_BLOCKED_ACTIONS,
            "AUTO_APPROVE_ORPHAN_REGISTRY_INCLUSION",
            "MERGE_ORPHAN_POLICY_INTO_REPAIR_CHAIN_CLOSURE",
        ],
        "acceptance_gates": [
            {
                "gate_id": "orphan_policy_operator_decision_required",
                "required_before": "any orphan registry inclusion or archive lane",
                "status": "READY_FOR_OPERATOR_DECISION" if review_ready else "BLOCKED",
            },
            {
                "gate_id": "orphan_policy_operator_review_hold",
                "required_before": "including orphan outputs in canonical registry repair",
                "status": "READY_FOR_OPERATOR_DECISION" if review_ready else "OPERATOR_HELD",
            },
            {
                "gate_id": "p130_advisory_hold_preservation_gate",
                "required_before": "any orphan policy that could imply P130 activation",
                "status": "ACTIVE",
            },
            {
                "gate_id": "separate_orphan_registry_governance_gate",
                "required_before": "merging orphan decisions into sealed repair chain",
                "status": "ACTIVE",
            },
        ],
        "decision_record_plan_candidates": [
            "out/operator_review/"
            "abx_research_canary_orphan_output_registry_policy_operator_decision_record_plan_001.latest.json",
            "out/operator_review/"
            "abx_research_canary_orphan_output_registry_policy_operator_decision_record_plan_001.latest.md",
        ],
        "follow_on_actions_if_exclude_maintained": [
            "SEAL_ORPHAN_POLICY_GOVERNANCE",
            "MAINTAIN_ORPHAN_EXCLUSION",
        ],
        "follow_on_actions_if_inclusion_authorized": [
            "AUTHOR_ORPHAN_REGISTRY_INCLUSION_EXECUTION_SPEC",
            "SEPARATE_ORPHAN_REGISTRY_GOVERNANCE",
        ],
        "follow_on_actions_if_archive_authorized": [
            "AUTHOR_ORPHAN_ARCHIVE_PLAN",
            "SEPARATE_ORPHAN_REGISTRY_GOVERNANCE",
        ],
        "follow_on_actions_if_held": [
            "MAINTAIN_ORPHAN_POLICY_HOLD",
            "WAIT_FOR_EXPLICIT_OPERATOR_DECISION_EVIDENCE",
        ],
        "blocked_reasons": [
            "FINAL_OPERATOR_DECISION_RECORD_MISSING",
            "ORPHAN_REGISTRY_INCLUSION_AUTHORITY_DENIED",
            "P130_ADVISORY_HOLD_MUST_BE_PRESERVED",
            "SEPARATE_ORPHAN_REGISTRY_GOVERNANCE_REQUIRED",
        ],
        "source_policy_review": {
            "source_policy_review_path": str(POLICY_REVIEW_JSON_PATH),
            "source_policy_review_hash": str(review.get("review_hash", NOT_COMPUTABLE)),
            "source_policy_review_status": str(review.get("status", NOT_COMPUTABLE)),
            "source_policy_review_observed": review_ready,
        },
        "recommended_next_lane": DECISION_RECORD_PLAN_LANE if review_ready else NOT_COMPUTABLE,
        "downstream_status": "READY_FOR_OPERATOR_DECISION_RECORD_PLAN" if review_ready else NOT_COMPUTABLE,
    }
    return {**packet, "request_hash": canonical_hash(packet)}


def render_abx_research_canary_orphan_output_registry_policy_operator_decision_request_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Research Canary Orphan Output Registry Policy Operator Decision Request 001",
        "",
        f"- `request_id`: `{packet['request_id']}`",
        f"- `status`: `{packet['status']}`",
        f"- `decision_scope`: `{packet['decision_scope']}`",
        f"- `recommended_decision`: `{packet['recommended_decision']}`",
        f"- `recommended_next_lane`: `{packet['recommended_next_lane']}`",
        f"- `recommended_next_action`: `{packet['recommended_next_action']}`",
        "",
        "## Acceptance Gates",
    ]
    for gate in packet.get("acceptance_gates", []):
        if isinstance(gate, dict):
            lines.append(f"- `{gate.get('gate_id')}`: `{gate.get('status')}`")
    lines.extend(["", "## Decision Options"])
    for option in packet.get("decision_options", []):
        lines.append(f"- `{option}`")
    return lines


def write_abx_research_canary_orphan_output_registry_policy_operator_decision_request(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_research_canary_orphan_output_registry_policy_operator_decision_request(root)
    write_canonical_json(target_root / OUT_JSON, packet)
    _write_markdown(
        target_root / OUT_MD,
        render_abx_research_canary_orphan_output_registry_policy_operator_decision_request_markdown(packet),
    )
    return packet
