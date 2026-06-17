from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_research_canary_artifact_registry_coverage_repair_spec_plan import (
    BLOCKED_ACTIONS as SPEC_PLAN_BLOCKED_ACTIONS,
    SPEC_PLAN_ID,
)
from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "AbxResearchCanaryArtifactRegistryCoverageRepairOperatorDecisionRequest.v1"
REQUEST_ID = "ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_REPAIR_OPERATOR_DECISION_REQUEST_001"
SOURCE_SPEC_PLAN_PATH = (
    "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_spec_plan_001.latest.json"
)
OUT_JSON = (
    "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_operator_decision_request_001.latest.json"
)
OUT_MD = (
    "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_operator_decision_request_001.latest.md"
)
PHASE_EXECUTION_RECEIPT_LANE = (
    "ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_REPAIR_PHASE_EXECUTION_RECEIPT_001"
)
NOT_COMPUTABLE = "NOT_COMPUTABLE"

DECISION_OPTIONS: tuple[str, ...] = (
    "HOLD",
    "AUTHORIZE_REGISTRY_REPAIR_EXECUTION_SPEC",
    "REQUEST_ORPHAN_POLICY_REVIEW",
    "REJECT_REGISTRY_REPAIR",
)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _validate_spec_plan(spec_plan: Mapping[str, Any]) -> bool:
    return (
        spec_plan.get("schema_version") == "AbxResearchCanaryArtifactRegistryCoverageRepairSpecPlan.v1"
        and spec_plan.get("spec_plan_id") == SPEC_PLAN_ID
        and spec_plan.get("spec_plan_status") == "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_SPEC_PLAN_READY"
        and spec_plan.get("registry_mutation_performed") is False
        and spec_plan.get("repair_execution_performed") is False
    )


def build_abx_research_canary_artifact_registry_coverage_repair_operator_decision_request(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    spec_plan = _read_json(root / SOURCE_SPEC_PLAN_PATH)
    spec_plan_ready = _validate_spec_plan(spec_plan)
    active_batch_count = int(spec_plan.get("active_repair_batch_count", 0))

    blocked_reasons = [
        "FINAL_OPERATOR_DECISION_RECORD_MISSING",
        "REGISTRY_REPAIR_EXECUTION_AUTHORITY_DENIED",
        "P130_ADVISORY_HOLD_MUST_BE_PRESERVED",
        "ORPHAN_RESEARCH_OUTPUT_POLICY_UNRESOLVED",
        "SCOPE_PREFIX_VS_DERIVED_OPTIONAL_POLICY_UNRESOLVED",
    ]

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": REQUEST_ID,
        "status": "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_OPERATOR_DECISION_REQUEST_EMITTED"
        if spec_plan_ready
        else "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_OPERATOR_DECISION_REQUEST_BLOCKED",
        "request_id": REQUEST_ID,
        "command": "BUILD_ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_REPAIR_OPERATOR_DECISION_REQUEST_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "evidence_only": True,
        "execution_authority": False,
        "promotion_allowed": False,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "registry_mutation_allowed": False,
        "repair_execution_performed": False,
        "registry_mutation_performed": False,
        "implementation_authorized": False,
        "spec_authoring_only_if_approved": True,
        "safe_to_auto_continue": False,
        "safe_to_prepare_planning_pr": False,
        "decision_scope": "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_DECISION_REQUIRED",
        "decision_question": (
            "Should Abraxas authorize a governed registry repair execution spec for P103-P130 "
            "research-canary lane visibility after the repair spec plan classified all registry gaps?"
        ),
        "target_surface": "ABX Research Canary Artifact Registry Coverage Repair",
        "target_plan_id": SPEC_PLAN_ID,
        "source_spec_plan_path": SOURCE_SPEC_PLAN_PATH,
        "spec_plan_ready": spec_plan_ready,
        "active_repair_batch_count": active_batch_count,
        "priority": "P0",
        "queue_action": "HOLD_FOR_GOVERNED_OPERATOR_DECISION",
        "decision_options": list(DECISION_OPTIONS),
        "recommended_decision": "HOLD",
        "recommended_next_action": (
            "review the repair spec plan batches, confirm orphan and scope-prefix policy holds, "
            "and collect explicit operator decision evidence before any registry repair execution"
            if spec_plan_ready
            else "repair the repair-spec-plan prerequisites before any operator decision can be considered"
        ),
        "required_operator_actions": [
            "review_repair_spec_plan_batches",
            "review_canonical_lane_output_path_gaps",
            "review_lane_id_traceability_gaps",
            "review_scope_prefix_vs_derived_optional_policy",
            "review_orphan_research_output_exclusion_policy",
            "confirm_p130_advisory_hold_preservation",
            "collect_registry_repair_operator_decision",
            "record_registry_repair_operator_decision",
        ],
        "required_evidence": [
            "repair_spec_plan_ready",
            "phase_execution_receipt_for_all_five_phases",
            "explicit_operator_decision_record",
            "p130_hold_boundary_acknowledgement",
        ],
        "blocked_actions": [
            *SPEC_PLAN_BLOCKED_ACTIONS,
            "DIRECT_REGISTRY_COVERAGE_REPAIR_EXECUTION",
            "AUTO_APPROVE_REGISTRY_REPAIR",
        ],
        "acceptance_gates": [
            {
                "gate_id": "research_canary_registry_repair_operator_decision_required",
                "required_before": "any P103-P130 registry repair execution",
                "status": "PENDING_OPERATOR_DECISION",
            },
            {
                "gate_id": "orphan_policy_operator_review_hold",
                "required_before": "including orphan outputs in registry repair",
                "status": "OPERATOR_HELD",
            },
            {
                "gate_id": "scope_prefix_policy_operator_review_hold",
                "required_before": "bulk scope-prefix registry normalization",
                "status": "OPERATOR_HELD",
            },
            {
                "gate_id": "p130_advisory_hold_preservation_gate",
                "required_before": "any registry repair that could imply P130 activation",
                "status": "ACTIVE",
            },
        ],
        "decision_record_plan_candidates": [
            "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_operator_decision_record_plan_001.latest.json",
            "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_operator_decision_record_plan_001.latest.md",
        ],
        "follow_on_actions_if_approved": [
            "AUTHOR_REGISTRY_REPAIR_EXECUTION_SPEC",
            "OPEN_REGISTRY_REPAIR_EXECUTION_PR",
        ],
        "follow_on_actions_if_held": [
            "MAINTAIN_REGISTRY_REPAIR_HOLD",
            "MAINTAIN_EXECUTION_DENIAL",
            "WAIT_FOR_EXPLICIT_OPERATOR_DECISION_EVIDENCE",
        ],
        "follow_on_actions_if_rejected": [
            "SEAL_RESEARCH_CANARY_REGISTRY_REPAIR_CHAIN_AS_ADVISORY_ONLY",
            "DO_NOT_PREPARE_REGISTRY_REPAIR_EXECUTION",
        ],
        "follow_on_actions_if_orphan_review_requested": [
            "REVIEW_ORPHAN_RESEARCH_OUTPUT_POLICY",
            "SEPARATE_ORPHAN_REGISTRY_GOVERNANCE",
        ],
        "blocked_reasons": blocked_reasons,
        "source_spec_plan": {
            "source_spec_plan_path": SOURCE_SPEC_PLAN_PATH,
            "source_spec_plan_hash": str(spec_plan.get("spec_plan_hash", NOT_COMPUTABLE)),
            "source_spec_plan_status": str(spec_plan.get("spec_plan_status", NOT_COMPUTABLE)),
            "source_spec_plan_observed": spec_plan_ready,
        },
        "recommended_next_lane": PHASE_EXECUTION_RECEIPT_LANE if spec_plan_ready else NOT_COMPUTABLE,
        "downstream_status": "READY_FOR_PHASE_EXECUTION_RECEIPT" if spec_plan_ready else NOT_COMPUTABLE,
    }
    return {**packet, "request_hash": canonical_hash(packet)}


def render_abx_research_canary_artifact_registry_coverage_repair_operator_decision_request_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Research Canary Artifact Registry Coverage Repair Operator Decision Request 001",
        "",
        f"- `request_id`: `{packet['request_id']}`",
        f"- `status`: `{packet['status']}`",
        f"- `decision_scope`: `{packet['decision_scope']}`",
        f"- `recommended_decision`: `{packet['recommended_decision']}`",
        f"- `recommended_next_lane`: `{packet['recommended_next_lane']}`",
        f"- `recommended_next_action`: `{packet['recommended_next_action']}`",
        "",
        "## Blocked Reasons",
    ]
    for reason in packet.get("blocked_reasons", []):
        lines.append(f"- `{reason}`")
    lines.extend(["", "## Decision Options"])
    for option in packet.get("decision_options", []):
        lines.append(f"- `{option}`")
    return lines


def write_abx_research_canary_artifact_registry_coverage_repair_operator_decision_request(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_research_canary_artifact_registry_coverage_repair_operator_decision_request(root)
    write_canonical_json(target_root / OUT_JSON, packet)
    (target_root / OUT_MD).parent.mkdir(parents=True, exist_ok=True)
    (target_root / OUT_MD).write_text(
        "\n".join(
            render_abx_research_canary_artifact_registry_coverage_repair_operator_decision_request_markdown(packet)
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
