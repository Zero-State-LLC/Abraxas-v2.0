from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_codegen_intelligence_spine_testing_validation_strategy_plan import (
    OUT_JSON as SOURCE_TESTING_STRATEGY_PLAN_JSON,
)
from core.abx_codegen_shadow_replay_harness_implementation_authorization_gate import (
    OUT_JSON as SOURCE_IMPLEMENTATION_AUTHORIZATION_GATE_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxCodegenIntelligenceSpineHarnessImplementationRoadmapPlan.v1"
PLAN_ID = "ABX_CODEGEN_INTELLIGENCE_SPINE_HARNESS_IMPLEMENTATION_ROADMAP_PLAN_001"
OUT_JSON = (
    "out/audit/"
    "abx_codegen_intelligence_spine_harness_implementation_roadmap_plan_001.latest.json"
)
OUT_MD = (
    "out/audit/"
    "abx_codegen_intelligence_spine_harness_implementation_roadmap_plan_001.latest.md"
)

NOTION_SPEC = {
    "title": "Harness Implementation Roadmap - Codegen Intelligence Spine",
    "page_id": "37d3e8ba-2f5c-8160-a6a4-e47bae761b2e",
    "observed_as_of": "2026-06-12",
    "status": "Implementation Planning",
    "based_on_page_id": "37d3e8ba-2f5c-8147-8aea-ccfd7be5d1e2",
    "phase_1_detail_page_id": "37d3e8ba-2f5c-813f-8ce3-d571c8736020",
}

EXPECTED_TESTING_STATUS = "ABX_CODEGEN_TESTING_VALIDATION_STRATEGY_PLAN_READY"
EXPECTED_AUTH_GATE_STATUS = "SHADOW_REPLAY_HARNESS_IMPLEMENTATION_AUTHORIZATION_HELD_FOR_OPERATOR"
GATE_GRANTED_STATUS = "SHADOW_REPLAY_HARNESS_IMPLEMENTATION_AUTHORIZATION_GRANTED"


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


def _phases(*, source_ready: bool, phase_1_authorized: bool) -> list[dict[str, Any]]:
    phases = _phase_definitions()
    for phase in phases:
        if phase_1_authorized and phase["phase"] == "Phase 1: Core Foundation":
            phase["phase_status"] = "AUTHORIZED_IN_PROGRESS"
            phase["implementation_authorized"] = True
        elif source_ready:
            phase["phase_status"] = "BLOCKED_PENDING_OPERATOR_AUTHORIZATION"
            phase["implementation_authorized"] = False
        else:
            phase["phase_status"] = "NOT_COMPUTABLE"
            phase["implementation_authorized"] = False
    return phases


def _phase_definitions() -> list[dict[str, Any]]:
    return [
        {
            "phase": "Phase 1: Core Foundation",
            "priority": "Highest",
            "goal": "Build a working end-to-end flow for normal non-self-modifying proposals",
            "tasks": [
                "Implement run_codegen_shadow_replay skeleton",
                "Build validate_proposal and basic schema validation",
                "Implement build_replay_config using shadow_validation_plan",
                "Create minimal deterministic replay executor",
                "Implement basic standard proof flag evaluation",
                "Build determine_recommendation and build_receipt",
                "Add canonical JSON output",
            ],
            "success_criteria": [
                "Simple ImprovementProposal.v1 can produce valid ShadowImprovementReceipt.v1",
                "12-run invariance works for simple cases",
                "All standard proof flags are evaluated",
            ],
            "estimated_complexity": "Medium",
        },
        {
            "phase": "Phase 2: Self-Modification & Meta-Gate Support",
            "priority": "High",
            "goal": "Handle self_modification_risk true proposals correctly",
            "tasks": [
                "Add codegen-specific proof flags",
                "Implement Meta-Gate branching logic in recommendation engine",
                "Increase replay run count for self-modification proposals",
                "Populate promotion_blockers correctly",
                "Force HOLD_FOR_META_GATE when appropriate",
                "Add extra invariant checks for Meta-Gate path",
            ],
            "success_criteria": [
                "Self-improvement proposals correctly route to HOLD_FOR_META_GATE",
                "promotion_blockers are populated with relevant reasons",
                "Extra invariants are enforced",
            ],
            "estimated_complexity": "High",
        },
        {
            "phase": "Phase 3: Robustness & Integration",
            "priority": "High",
            "goal": "Make the harness production-ready and well-integrated",
            "tasks": [
                "Full error taxonomy implementation",
                "Proper integration with existing P103 replay logic",
                "Artifact Registry registration hooks",
                "Continuity lane creation hooks",
                "Comprehensive test suite including adversarial fixtures",
                "Performance optimization for replay execution",
                "Documentation and inline comments",
            ],
            "success_criteria": [
                "All error types handled gracefully",
                "Full test coverage on golden and adversarial cases",
                "Clean integration with Artifact Registry and Continuity Spine",
            ],
            "estimated_complexity": "High",
        },
        {
            "phase": "Phase 4: Advanced Features",
            "priority": "Future",
            "goal": "Track future feature families without granting implementation authority",
            "tasks": [
                "Support complex contract_deltas simulation",
                "Advanced visualization hooks for AAL-Viz",
                "Rune/YGGDRASIL integration points",
                "Operator tooling interfaces",
            ],
            "success_criteria": [],
            "estimated_complexity": "Future",
        },
    ]


def build_abx_codegen_intelligence_spine_harness_implementation_roadmap_plan(
    *,
    repo_root: str | Path,
    source_testing_validation_strategy_plan_path: str | Path = SOURCE_TESTING_STRATEGY_PLAN_JSON,
    source_implementation_authorization_gate_path: str | Path = SOURCE_IMPLEMENTATION_AUTHORIZATION_GATE_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    testing_path = Path(source_testing_validation_strategy_plan_path).as_posix()
    auth_path = Path(source_implementation_authorization_gate_path).as_posix()
    testing = _read_json(root / source_testing_validation_strategy_plan_path)
    auth = _read_json(root / source_implementation_authorization_gate_path)
    testing_ready = (
        testing.get("artifact_type")
        == "AbxCodegenIntelligenceSpineTestingValidationStrategyPlan.v1"
        and testing.get("testing_validation_strategy_plan_status") == EXPECTED_TESTING_STATUS
        and testing.get("recommended_next_lane") == "NOT_COMPUTABLE"
        and testing.get("safe_to_auto_continue") is False
        and testing.get("valid_for_implementation") is False
    )
    auth_held = (
        auth.get("artifact_type")
        == "AbxCodegenIntelligenceSpineShadowReplayHarnessImplementationAuthorizationGate.v1"
        and auth.get("authorization_gate_status") == EXPECTED_AUTH_GATE_STATUS
        and auth.get("implementation_authorization_granted") is False
        and auth.get("operator_review_required") is True
        and auth.get("valid_for_implementation") is False
    )
    auth_granted = (
        auth.get("artifact_type")
        == "AbxCodegenIntelligenceSpineShadowReplayHarnessImplementationAuthorizationGate.v1"
        and auth.get("authorization_gate_status") == GATE_GRANTED_STATUS
        and auth.get("implementation_authorization_granted") is True
        and auth.get("valid_for_implementation") is True
    )
    source_ready = testing_ready and (auth_held or auth_granted)
    phase_1_authorized = testing_ready and auth_granted

    if phase_1_authorized:
        plan_status = "ABX_CODEGEN_HARNESS_IMPLEMENTATION_ROADMAP_PLAN_AUTHORIZED"
        starting_point = {
            "notion_recommended_phase": "Phase 1: Core Foundation",
            "repo_authorized_starting_point": "PHASE_1_CORE_FOUNDATION",
            "minimal_working_loop_authorized": True,
            "phase_1_detail_code_authorized": True,
            "reason": "implementation authorization gate granted for Phase 1 only",
        }
        roadmap_blockers = [
            "phase_2_plus_pending_separate_authorization",
            "shadow_replay_execution_authority_denied",
            "runtime_mutation_authority_denied",
        ]
        valid_for_implementation = True
        harness_implementation_lock = True
        recommended_next_lane = "CORE_CODEGEN_SHADOW_REPLAY_HARNESS_IMPLEMENTATION"
    elif source_ready:
        plan_status = "ABX_CODEGEN_HARNESS_IMPLEMENTATION_ROADMAP_PLAN_HELD_FOR_OPERATOR"
        starting_point = {
            "notion_recommended_phase": "Phase 1: Core Foundation",
            "repo_authorized_starting_point": "NOT_AUTHORIZED",
            "minimal_working_loop_authorized": False,
            "phase_1_detail_code_authorized": False,
            "reason": "implementation authorization gate is held for operator review",
        }
        roadmap_blockers = [
            "implementation_authorization_gate_held_for_operator",
            "valid_for_implementation_false",
            "harness_implementation_authority_denied",
            "shadow_replay_execution_authority_denied",
        ]
        valid_for_implementation = False
        harness_implementation_lock = False
        recommended_next_lane = "NOT_COMPUTABLE"
    else:
        plan_status = "NOT_COMPUTABLE"
        starting_point = {
            "notion_recommended_phase": "Phase 1: Core Foundation",
            "repo_authorized_starting_point": "NOT_AUTHORIZED",
            "minimal_working_loop_authorized": False,
            "phase_1_detail_code_authorized": False,
            "reason": "required upstream sources missing or not ready",
        }
        roadmap_blockers = ["upstream_sources_not_ready"]
        valid_for_implementation = False
        harness_implementation_lock = False
        recommended_next_lane = "NOT_COMPUTABLE"

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "harness_implementation_roadmap_plan_status": plan_status,
        "source_notion_spec": {
            **NOTION_SPEC,
            "spec_hash_policy": "source_observed_metadata_only",
            "notion_writeback_performed": False,
        },
        "source_testing_validation_strategy_plan": {
            "path": testing_path,
            "hash": _sha256(root / source_testing_validation_strategy_plan_path),
            "testing_validation_strategy_plan_status": str(
                testing.get("testing_validation_strategy_plan_status", "NOT_COMPUTABLE")
            ),
            "source_ready": testing_ready,
        },
        "implementation_authorization_source": {
            "path": auth_path,
            "hash": _sha256(root / source_implementation_authorization_gate_path),
            "authorization_gate_status": str(
                auth.get("authorization_gate_status", "NOT_COMPUTABLE")
            ),
            "implementation_authorization_granted": auth.get(
                "implementation_authorization_granted"
            )
            is True,
            "operator_review_required": auth.get("operator_review_required") is True,
            "source_ready": auth_held or auth_granted,
        },
        "phases": _phases(source_ready=source_ready, phase_1_authorized=phase_1_authorized),
        "recommended_starting_point": starting_point,
        "roadmap_blockers": roadmap_blockers,
        "recommended_next_lane": recommended_next_lane,
        "safe_to_auto_continue": False,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "valid_for_execution": False,
        "valid_for_implementation": valid_for_implementation,
        "authority_locks": {
            "advanced_feature_implementation": False,
            "artifact_registry_hooks": False,
            "auto_approval": False,
            "canon_mutation": False,
            "code_generation": False,
            "code_mutation": False,
            "continuity_lane_hooks": False,
            "dependency_addition": False,
            "file_writeback": False,
            "forecast_routing": False,
            "github_writeback": False,
            "harness_implementation": harness_implementation_lock,
            "meta_gate_authorization": False,
            "meta_gate_branching_implementation": False,
            "notion_writeback": False,
            "operator_tooling_interfaces": False,
            "p103_replay_refactor": False,
            "queue_mutation": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
            "shadow_replay_execution": False,
            "test_suite_implementation": False,
        },
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_abx_codegen_intelligence_spine_harness_implementation_roadmap_plan(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_abx_codegen_intelligence_spine_harness_implementation_roadmap_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Codegen Intelligence Spine Harness Implementation Roadmap Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        f"- harness_implementation_roadmap_plan_status: {packet['harness_implementation_roadmap_plan_status']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- execution_authority: {packet['execution_authority']}",
        f"- valid_for_implementation: {packet['valid_for_implementation']}",
        "",
        "## Phases",
    ]
    for phase in packet.get("phases", []):
        if isinstance(phase, Mapping):
            lines.append(
                f"- {phase['phase']}: {phase['phase_status']} "
                f"(implementation_authorized={phase['implementation_authorized']})"
            )
    lines.extend(["", "## Roadmap Blockers"])
    for blocker in packet.get("roadmap_blockers", []):
        lines.append(f"- {blocker}")
    return lines


def write_abx_codegen_intelligence_spine_harness_implementation_roadmap_plan_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(
            render_abx_codegen_intelligence_spine_harness_implementation_roadmap_plan_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
