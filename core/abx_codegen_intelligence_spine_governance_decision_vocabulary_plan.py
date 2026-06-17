from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_codegen_intelligence_spine_shadow_replay_integration_exploration_plan import (
    OUT_JSON as SOURCE_SHADOW_REPLAY_INTEGRATION_EXPLORATION_PLAN_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxCodegenIntelligenceSpineGovernanceDecisionVocabularyPlan.v1"
PLAN_ID = "ABX_CODEGEN_INTELLIGENCE_SPINE_GOVERNANCE_DECISION_VOCABULARY_PLAN_001"
OUT_JSON = (
    "out/audit/"
    "abx_codegen_intelligence_spine_governance_decision_vocabulary_plan_001.latest.json"
)
OUT_MD = (
    "out/audit/"
    "abx_codegen_intelligence_spine_governance_decision_vocabulary_plan_001.latest.md"
)

EXPECTED_SOURCE_STATUS = "ABX_CODEGEN_SHADOW_REPLAY_INTEGRATION_EXPLORATION_PLAN_HELD_FOR_OPERATOR"

NOTION_SPEC = {
    "title": "Abraxas Governance Decision Vocabulary - HOLD vs BLOCK Patterns",
    "page_id": "37d3e8ba-2f5c-812a-8fe3-c1d89f2847e1",
    "observed_as_of": "2026-06-12",
    "status": "Reference Surface (Advisory)",
    "version": "source_observed",
    "timestamp_policy": "source_observed_date_only_no_wall_clock_generation",
}


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return "NOT_COMPUTABLE"


def _read_json(path: Path) -> Mapping[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _planning_status(source_ready: bool) -> str:
    return "VOCABULARY_DEFINED_HELD_FOR_OPERATOR" if source_ready else "NOT_COMPUTABLE"


def build_abx_codegen_intelligence_spine_governance_decision_vocabulary_plan(
    *,
    repo_root: str | Path,
    source_shadow_replay_integration_exploration_plan_path: str
    | Path = SOURCE_SHADOW_REPLAY_INTEGRATION_EXPLORATION_PLAN_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_shadow_replay_integration_exploration_plan_path).as_posix()
    source = _read_json(root / source_shadow_replay_integration_exploration_plan_path)
    source_ready = (
        source.get("artifact_type")
        == "AbxCodegenIntelligenceSpineShadowReplayIntegrationExplorationPlan.v1"
        and source.get("shadow_replay_integration_exploration_plan_status")
        == EXPECTED_SOURCE_STATUS
        and source.get("recommended_next_lane") == "NOT_COMPUTABLE"
        and source.get("safe_to_auto_continue") is False
        and source.get("execution_authority") is False
        and source.get("valid_for_implementation") is False
    )
    status = _planning_status(source_ready)

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "governance_decision_vocabulary_plan_status": (
            "ABX_CODEGEN_GOVERNANCE_DECISION_VOCABULARY_PLAN_HELD_FOR_OPERATOR"
            if source_ready
            else "NOT_COMPUTABLE"
        ),
        "source_notion_spec": {**NOTION_SPEC, "notion_writeback_performed": False},
        "source_shadow_replay_integration_exploration_plan": {
            "path": source_path,
            "hash": _sha256(root / source_shadow_replay_integration_exploration_plan_path),
            "shadow_replay_integration_exploration_plan_status": str(
                source.get("shadow_replay_integration_exploration_plan_status", "NOT_COMPUTABLE")
            ),
            "source_ready": source_ready,
        },
        "hold_block_distinctions": [
            {
                "term": "HOLD_FOR_OPERATOR",
                "meaning": "temporary_pause_pending_operator_review_or_additional_evidence",
                "typical_triggers": [
                    "missing_proof",
                    "high_risk",
                    "replay_incomplete",
                ],
                "recovery_path": "operator_decision_record_or_additional_evidence",
                "distinction_status": status,
                "routing_authorized": False,
            },
            {
                "term": "HOLD_FOR_META_GATE",
                "meaning": "specialized_hold_for_self_modification_or_core_governance_change",
                "typical_triggers": ["self_modification_detected", "core_surface_targeted"],
                "recovery_path": "meta_gate_authorization_chain_plus_elevated_operator_review",
                "distinction_status": status,
                "routing_authorized": False,
            },
            {
                "term": "BLOCK_POLICY_VIOLATION",
                "meaning": "hard_stop_for_policy_or_authority_boundary_violation",
                "typical_triggers": [
                    "authority_drift",
                    "governance_compliance_failed",
                    "red_zone_surface_targeted",
                ],
                "recovery_path": "new_or_substantially_remediated_proposal",
                "distinction_status": status,
                "routing_authorized": False,
            },
            {
                "term": "BLOCK_REPLAY_FAILURE",
                "meaning": "hard_stop_for_replay_failure_or_unmet_replay_proofs",
                "typical_triggers": ["replay_hash_divergence", "missing_proof_flags"],
                "recovery_path": "replay_remediation_or_refined_proposal",
                "distinction_status": status,
                "routing_authorized": False,
            },
        ],
        "recommended_decision_enum": [
            {
                "value": "PROMOTE_TO_CANARY",
                "classification": "promotion_candidate",
                "promotion_blockers_required": False,
                "enum_status": status,
            },
            {
                "value": "HOLD_FOR_OPERATOR",
                "classification": "temporary_hold",
                "promotion_blockers_required": True,
                "enum_status": status,
            },
            {
                "value": "HOLD_FOR_META_GATE",
                "classification": "self_improvement_hold",
                "promotion_blockers_required": True,
                "enum_status": status,
            },
            {
                "value": "BLOCK_POLICY_VIOLATION",
                "classification": "hard_block",
                "promotion_blockers_required": True,
                "enum_status": status,
            },
            {
                "value": "BLOCK_REPLAY_FAILURE",
                "classification": "hard_block",
                "promotion_blockers_required": True,
                "enum_status": status,
            },
            {
                "value": "REJECT",
                "classification": "terminal_rejection",
                "promotion_blockers_required": True,
                "enum_status": status,
            },
            {
                "value": "REFINE_PROPOSAL",
                "classification": "revision_request",
                "promotion_blockers_required": True,
                "enum_status": status,
            },
        ],
        "promotion_blocker_policy": {
            "policy_status": status,
            "required_when_recommendation_not_promote_to_canary": True,
            "machine_readable_reasons_required": True,
            "example_blockers": [
                "self_modification_detected",
                "replay_hash_divergence",
                "missing_proof_flags",
                "governance_compliance_failed",
                "high_governance_rent_without_meta_gate",
            ],
            "blocker_population_authorized": False,
        },
        "self_modification_policy": {
            "policy_status": status,
            "self_modification_risk_recommendation": "HOLD_FOR_META_GATE",
            "must_hold": True,
            "dedicated_meta_gate_authorization_chain_required": True,
            "direct_promotion_allowed": False,
            "routing_authorized": False,
        },
        "usage_guidance": [
            {
                "guidance": "use_hold_for_meta_gate_when_self_modification_risk_true",
                "guidance_status": status,
                "implementation_authorized": False,
            },
            {
                "guidance": "populate_promotion_blockers_for_any_hold_block_reject_or_refine",
                "guidance_status": status,
                "implementation_authorized": False,
            },
            {
                "guidance": "keep_temporary_holds_distinct_from_hard_blocks",
                "guidance_status": status,
                "implementation_authorized": False,
            },
            {
                "guidance": "hard_blocks_require_remediation_or_new_proposal",
                "guidance_status": status,
                "implementation_authorized": False,
            },
        ],
        "implementation_blockers": [
            "shadow_replay_integration_exploration_plan_held_for_operator",
            "receipt_schema_mutation_denied",
            "recommendation_routing_denied",
            "promotion_blocker_population_denied",
            "operator_decision_record_creation_denied",
            "meta_gate_chain_creation_denied",
            "artifact_registry_registration_denied",
            "notion_writeback_denied",
            "github_writeback_denied",
        ],
        "recommended_next_lane": "NOT_COMPUTABLE",
        "safe_to_auto_continue": False,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "authority_locks": {
            "artifact_registry_registration": False,
            "auto_approval": False,
            "canary_promotion": False,
            "canon_mutation": False,
            "code_generation": False,
            "code_mutation": False,
            "execution": False,
            "file_writeback": False,
            "forecast_routing": False,
            "github_writeback": False,
            "meta_gate_chain_creation": False,
            "notion_writeback": False,
            "operator_decision_record_creation": False,
            "promotion_blocker_population": False,
            "queue_mutation": False,
            "receipt_creation": False,
            "receipt_schema_mutation": False,
            "recommendation_routing": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
        },
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_abx_codegen_intelligence_spine_governance_decision_vocabulary_plan(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_abx_codegen_intelligence_spine_governance_decision_vocabulary_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Codegen Intelligence Spine Governance Decision Vocabulary Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        "- governance_decision_vocabulary_plan_status: "
        f"{packet['governance_decision_vocabulary_plan_status']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- execution_authority: {packet['execution_authority']}",
        f"- valid_for_implementation: {packet['valid_for_implementation']}",
        "",
        "## Decision Enum",
    ]
    for item in packet.get("recommended_decision_enum", []):
        if isinstance(item, Mapping):
            lines.append(
                f"- {item['value']}: {item['classification']} "
                f"(promotion_blockers_required={item['promotion_blockers_required']})"
            )
    lines.extend(["", "## HOLD vs BLOCK"])
    for item in packet.get("hold_block_distinctions", []):
        if isinstance(item, Mapping):
            lines.append(
                f"- {item['term']}: {item['meaning']} "
                f"(routing_authorized={item['routing_authorized']})"
            )
    lines.extend(["", "## Implementation Blockers"])
    for blocker in packet.get("implementation_blockers", []):
        lines.append(f"- {blocker}")
    return lines


def write_abx_codegen_intelligence_spine_governance_decision_vocabulary_plan_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(
            render_abx_codegen_intelligence_spine_governance_decision_vocabulary_plan_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
