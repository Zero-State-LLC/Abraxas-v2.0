from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_codegen_intelligence_spine_merge_anchor_evidence_request_plan import (
    OUT_JSON as SOURCE_MERGE_ANCHOR_EVIDENCE_REQUEST_PLAN_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxCodegenIntelligenceSpineMergeAnchorEvidenceNormalizationPlan.v1"
PLAN_ID = "ABX_CODEGEN_INTELLIGENCE_SPINE_MERGE_ANCHOR_EVIDENCE_NORMALIZATION_PLAN_001"
OUT_JSON = (
    "out/audit/"
    "abx_codegen_intelligence_spine_merge_anchor_evidence_normalization_plan_001.latest.json"
)
OUT_MD = (
    "out/audit/"
    "abx_codegen_intelligence_spine_merge_anchor_evidence_normalization_plan_001.latest.md"
)

EXPECTED_REQUEST_STATUS = (
    "ABX_CODEGEN_MERGE_ANCHOR_EVIDENCE_REQUEST_PLAN_HELD_FOR_OPERATOR"
)

NORMALIZED_ANCHOR_EVIDENCE: list[dict[str, Any]] = [
    {
        "anchor_id": "codegen_upgrade_v0_1_v0_2",
        "normalization_status": "NORMALIZED_FROM_EXACT_NOTION_PAGE_HELD_FOR_OPERATOR",
        "source_title": "Abraxas CodeGen Upgrade v0.1-v0.2 - Coding Intelligence Canon-Shadow",
        "source_observed_title": "Abraxas CodeGen Upgrade v0.1-v0.2 - Coding Intelligence Canon-Shadow",
        "notion_page_id_or_url": "34f3e8ba-2f5c-81f2-b3b3-fdf91dd8d8c4",
        "source_observed_at": "2026-04-27T16:02:34.135Z",
        "source_role": "historical_codegen_doctrine",
        "governance_posture": "CANON_SHADOW",
        "authority_boundaries": [
            "runtime_authority_shadow_only",
            "promotion_requires_tests_canary_governance",
            "mock_data_not_allowed",
        ],
        "merge_rules": [
            "treat_as_historical_doctrine_evidence",
            "do_not_import_repo_file_list_as_current_required_implementation",
        ],
        "repo_relevance_summary": (
            "Defines early CodeGen contracts, adversarial scan, ledger, canary, "
            "and replay concepts as shadow-only source doctrine."
        ),
        "implementation_constraints": [
            "generated_code_not_promoted_by_default",
            "promotion_candidate_requires_adversarial_pass_golden_tests_canary_stability",
        ],
        "evidence_hash_policy": "hash_source_page_id_title_observed_at_and_summary",
        "operator_review_requirement": "operator_must_confirm_before_implementation_unblock",
    },
    {
        "anchor_id": "codegen_upgrade_v0_4",
        "normalization_status": "NORMALIZED_FROM_EXACT_NOTION_PAGE_HELD_FOR_OPERATOR",
        "source_title": "Abraxas CodeGen Upgrade v0.4 - Autonomous Patch Loop + Promotion Gate",
        "source_observed_title": "Abraxas CodeGen Upgrade v0.4 - Autonomous Patch Loop + Promotion Gate",
        "notion_page_id_or_url": "34f3e8ba-2f5c-812a-8f3d-f38607f8bb1a",
        "source_observed_at": "2026-04-27T16:03:53.184Z",
        "source_role": "historical_codegen_patch_loop_doctrine",
        "governance_posture": "CANON_SHADOW",
        "authority_boundaries": [
            "patch_loop_shadow_only",
            "promotion_gate_shadow_only",
            "patch_apply_shadow_only",
            "may_emit_recommendation_only",
        ],
        "merge_rules": [
            "preserve_no_self_promotion_boundary",
            "preserve_no_main_merge_or_canonical_policy_mutation_boundary",
        ],
        "repo_relevance_summary": (
            "Defines deterministic patch-loop concepts and promotion recommendation "
            "rules without granting merge, policy, or self-promotion authority."
        ),
        "implementation_constraints": [
            "may_not_merge_to_main",
            "may_not_mutate_canonical_policy",
            "may_not_bypass_canary",
            "may_not_bypass_operator_governance",
            "may_not_mark_itself_canon_active",
        ],
        "evidence_hash_policy": "hash_source_page_id_title_observed_at_and_summary",
        "operator_review_requirement": "operator_must_confirm_any_patch_loop_contract_scope",
    },
    {
        "anchor_id": "codegen_upgrade_v0_7",
        "normalization_status": "NORMALIZED_FROM_EXACT_NOTION_PAGE_HELD_FOR_OPERATOR",
        "source_title": (
            "Abraxas CodeGen Upgrade v0.7 - Adversarial Policy Generator + "
            "Red-Team Mutation Harness"
        ),
        "source_observed_title": (
            "Abraxas CodeGen Upgrade v0.7 - Adversarial Policy Generator + "
            "Red-Team Mutation Harness"
        ),
        "notion_page_id_or_url": "34f3e8ba-2f5c-81b5-ab1c-e3012cfba91d",
        "source_observed_at": "2026-04-27T16:09:04.934Z",
        "source_role": "historical_codegen_adversarial_policy_doctrine",
        "governance_posture": "CANON_SHADOW",
        "authority_boundaries": [
            "adversarial_policy_generation_for_defensive_validation_only",
            "red_team_harness_shadow_only",
            "unsafe_policy_application_forbidden",
        ],
        "merge_rules": [
            "retain_defensive_testing_scope",
            "do_not_persist_generated_policy_as_active_policy",
        ],
        "repo_relevance_summary": (
            "Defines red-team policy mutation probes that must be blocked by "
            "firewall, canary, or evolution gates."
        ),
        "implementation_constraints": [
            "may_not_apply_policy",
            "may_not_promote_policy",
            "may_not_persist_as_active_policy",
            "may_not_execute_unsafe_behaviors",
        ],
        "evidence_hash_policy": "hash_source_page_id_title_observed_at_and_summary",
        "operator_review_requirement": "operator_must_confirm_defensive_harness_scope",
    },
    {
        "anchor_id": "codeir_v1_1",
        "normalization_status": "NORMALIZED_FROM_EXACT_NOTION_PAGE_HELD_FOR_OPERATOR",
        "source_title": "Abraxas CodeIR v1.1 - ABX-Native Design Doctrine + Profundity Gate",
        "source_observed_title": (
            "Abraxas CodeIR v1.1 - ABX-Native Design Doctrine + Profundity Gate"
        ),
        "notion_page_id_or_url": "34f3e8ba-2f5c-8110-832f-fd0180b60301",
        "source_observed_at": "2026-04-27T17:04:28.589Z",
        "source_role": "design_doctrine",
        "governance_posture": "CANON_SHADOW_TO_CANARY_ELIGIBLE",
        "authority_boundaries": [
            "design_quality_gate_only",
            "may_block_generic_implementations",
            "may_not_bypass_proof_gates",
            "may_not_promote_code",
        ],
        "merge_rules": [
            "candidate_must_bind_to_rune_yggdrasil_seed_and_lane_boundaries",
            "missing_core_law_answers_route_to_hold_or_block",
        ],
        "repo_relevance_summary": (
            "Requires Codegen outputs to be Abraxas-native through rune binding, "
            "YGGDRASIL placement, provenance, lane safety, and governance."
        ),
        "implementation_constraints": [
            "generic_code_allowed_only_as_substrate",
            "must_answer_rune_yggdrasil_failure_reduction_and_abraxas_specificity",
        ],
        "evidence_hash_policy": "hash_source_page_id_title_observed_at_and_summary",
        "operator_review_requirement": "operator_must_confirm_design_gate_mapping",
    },
    {
        "anchor_id": "prompting_upgrade_stack_v0_1",
        "normalization_status": "AMBIGUOUS_SEARCH_RESULT_HELD_FOR_OPERATOR",
        "source_title": "ABX Prompting Upgrade Stack v0.1 - Canon-Shadow",
        "source_observed_title": "NOT_COMPUTABLE",
        "notion_page_id_or_url": "NOT_COMPUTABLE",
        "source_observed_at": "NOT_COMPUTABLE",
        "source_role": "prompting_doctrine",
        "governance_posture": "REFERENCED_BY_CODEGEN_FORMALIZATION_ONLY",
        "authority_boundaries": [
            "canonical_source_page_not_resolved",
            "no_prompting_doctrine_import_authorized",
        ],
        "merge_rules": [
            "require_operator_supplied_canonical_page_or_url",
            "do_not_substitute_master_system_or_codegen_formalization_reference",
        ],
        "repo_relevance_summary": (
            "Search found references to the prompting stack but did not resolve a "
            "single exact canonical source page."
        ),
        "implementation_constraints": [
            "prompt_emission_remains_blocked",
            "prompting_stack_scope_not_implementation_ready",
        ],
        "evidence_hash_policy": "NOT_COMPUTABLE_UNTIL_CANONICAL_SOURCE_SELECTED",
        "operator_review_requirement": "operator_must_select_or_provide_canonical_prompting_stack_source",
    },
    {
        "anchor_id": "code_drop_envelope_rule",
        "normalization_status": "CANDIDATE_SOURCE_NORMALIZED_HELD_FOR_OPERATOR",
        "source_title": "ABX Code Drop Envelope rule",
        "source_observed_title": "ABX Code Drop Envelope - abx-familiar v0.1",
        "notion_page_id_or_url": "82996cf1-0784-4114-ab44-eccb5b054a09",
        "source_observed_at": "2026-01-27T02:18:39.936Z",
        "source_role": "code_drop_doctrine_candidate",
        "governance_posture": "SHADOW",
        "authority_boundaries": [
            "candidate_source_only",
            "governance_modules_flag_only",
            "runtime_emits_partial_artifacts_on_failure",
        ],
        "merge_rules": [
            "require_operator_confirmation_because_multiple_code_drop_pages_exist",
            "do_not_treat_candidate_page_as_global_rule_until_confirmed",
        ],
        "repo_relevance_summary": (
            "Provides a concrete Code Drop Envelope candidate with SHADOW lane, "
            "required files, implementation rules, tests, and exit criteria."
        ),
        "implementation_constraints": [
            "all_ir_objects_hashable",
            "unknown_values_explicitly_flagged",
            "agents_do_not_mutate_other_agent_outputs",
            "all_outputs_typed_and_legered",
        ],
        "evidence_hash_policy": "hash_candidate_source_page_id_title_observed_at_and_summary",
        "operator_review_requirement": "operator_must_confirm_global_code_drop_envelope_source",
    },
    {
        "anchor_id": "incremental_patch_only_doctrine",
        "normalization_status": "NORMALIZED_FROM_SYSTEM_STATE_REFERENCE_HELD_FOR_OPERATOR",
        "source_title": "Incremental Patch Only doctrine",
        "source_observed_title": "Abraxas - System State Snapshot (Authoritative)",
        "notion_page_id_or_url": "29a45e68-021c-4965-8fd8-3178ee3dfda6",
        "source_observed_at": "2026-04-23T03:05:44.740Z",
        "source_role": "patch_scope_doctrine_reference",
        "governance_posture": "CANON_ACTIVE_SYSTEM_STATE_REFERENCE",
        "authority_boundaries": [
            "additive_patches_allowed",
            "rewrites_require_justification",
            "notion_must_match_repo",
        ],
        "merge_rules": [
            "treat_as_system_state_reference_not_standalone_doctrine_page",
            "preserve_no_rewrites_without_justification",
        ],
        "repo_relevance_summary": (
            "System snapshot lists Incremental Patch Only as an active governance "
            "layer and an executor constraint."
        ),
        "implementation_constraints": [
            "additive_patches_only",
            "schema_first_changes",
            "explicit_assumptions",
            "no_hidden_coupling",
        ],
        "evidence_hash_policy": "hash_source_page_id_title_observed_at_and_summary",
        "operator_review_requirement": "operator_must_confirm_if_a_standalone_doctrine_source_exists",
    },
    {
        "anchor_id": "subsystem_merge_map_002",
        "normalization_status": "CANDIDATE_SOURCE_NORMALIZED_HELD_FOR_OPERATOR",
        "source_title": "ABRAXAS_SUBSYSTEM_MERGE_MAP_002",
        "source_observed_title": "Abraxas + AAL - Canon Surfaces Merge Map v1.0",
        "notion_page_id_or_url": "3553e8ba-2f5c-8111-ba0a-d9fb4a121906",
        "source_observed_at": "2026-05-03T15:19:47.702Z",
        "source_role": "merge_map_candidate",
        "governance_posture": "CANON_SHADOW_PENDING_OPERATOR_REVIEW",
        "authority_boundaries": [
            "consolidation_map_only",
            "does_not_supersede_root_canon",
            "no_lane_collapse",
        ],
        "merge_rules": [
            "do_not_merge_runtime_logs_into_identity_pages",
            "do_not_let_projection_pages_redefine_architecture",
            "do_not_let_integration_pages_imply_registry_promotion",
            "do_not_create_duplicate_doctrine_pages_when_link_compression_or_projection_suffices",
            "each_page_must_declare_one_primary_surface_role",
            "shadow_and_forecast_must_remain_distinct",
        ],
        "repo_relevance_summary": (
            "Candidate merge map routes identity, registry, state, governance, "
            "projection, and execution questions to separate surfaces."
        ),
        "implementation_constraints": [
            "preserve_identity_registry_projection_execution_role_boundaries",
            "do_not_claim_registry_promotion_from_integration_evidence",
        ],
        "evidence_hash_policy": "hash_candidate_source_page_id_title_observed_at_and_summary",
        "operator_review_requirement": "operator_must_confirm_this_candidate_maps_to_subsystem_merge_map_002",
    },
    {
        "anchor_id": "rune_promotion_gate",
        "normalization_status": "NORMALIZED_FROM_EXACT_NOTION_PAGE_HELD_FOR_OPERATOR",
        "source_title": "RUNE.PROMOTION_GATE - SHADOW to FORECAST Bridge Contract",
        "source_observed_title": "RUNE.PROMOTION_GATE - SHADOW to FORECAST Bridge Contract (RPG)",
        "notion_page_id_or_url": "3523e8ba-2f5c-814e-a011-d87765678d34",
        "source_observed_at": "2026-05-04T19:28:40.959Z",
        "source_role": "rune_contract_doctrine",
        "governance_posture": "CANON_SHADOW_ACTIVE_PIPELINE_SPEC",
        "authority_boundaries": [
            "bridge_gate_not_promotion_itself",
            "direct_forecast_mutation_false",
            "direct_execution_authority_false",
            "bypass_governance_false",
            "operator_approval_required",
        ],
        "merge_rules": [
            "no_subsystem_may_self_promote",
            "no_symbolic_resemblance_may_promote",
            "no_unscored_signal_may_promote",
            "no_promotion_may_bypass_replay_outcome_scoring_calibration_stability_operator_governance",
        ],
        "repo_relevance_summary": (
            "Defines the only allowed bridge from SHADOW observation to FORECAST "
            "candidacy and keeps direct mutation/execution authority false."
        ),
        "implementation_constraints": [
            "codegen_may_not_emit_forecast_authority",
            "promotion_review_required_before_any_authority_transition",
            "starting_forecast_weight_zero_until_approved",
        ],
        "evidence_hash_policy": "hash_source_page_id_title_observed_at_and_summary",
        "operator_review_requirement": "operator_must_confirm_any_promotion_gate_binding",
    },
    {
        "anchor_id": "system_state_snapshot_authoritative",
        "normalization_status": "NORMALIZED_WITH_REGISTRY_ALIAS_HELD_FOR_OPERATOR",
        "source_title": "Abraxas - System State Snapshot (Authoritative)",
        "source_observed_title": "Abraxas - System State Snapshot (Authoritative)",
        "notion_page_id_or_url": "29a45e68-021c-4965-8fd8-3178ee3dfda6",
        "source_observed_at": "2026-04-23T03:05:44.740Z",
        "source_role": "authoritative_system_state",
        "governance_posture": "CANON_ACTIVE_WITH_REGISTRY_ALIAS",
        "authority_boundaries": [
            "source_page_declares_authoritative_state",
            "registry_alias_points_back_to_source_page",
            "repo_visible_state_still_governs_repo_claims",
        ],
        "merge_rules": [
            "use_content_bearing_source_page_as_evidence",
            "track_registry_alias_as_alias_not_second_truth",
            "do_not_override_repo_evidence_from_notion_only_state",
        ],
        "repo_relevance_summary": (
            "Content-bearing system snapshot defines current state and patch policy; "
            "a registry row with the same title points back to this source page."
        ),
        "implementation_constraints": [
            "repo_encodes_governance_expectations",
            "notion_alignment_must_not_override_repo_artifact_evidence",
        ],
        "evidence_hash_policy": "hash_source_page_id_title_observed_at_and_summary",
        "operator_review_requirement": "operator_must_confirm_alias_relationship_before_authoritative_use",
        "aliases": [
            {
                "alias_page_id_or_url": "3553e8ba-2f5c-81fa-8721-c98f5398fe59",
                "alias_observed_at": "2026-05-03T15:33:36.077Z",
                "alias_role": "registry_row_points_to_source_page",
            }
        ],
    },
]

BLOCKED_ACTIONS = [
    "notion_writeback",
    "canonical_source_selection",
    "notion_anchor_mutation",
    "repo_anchor_file_creation",
    "merge_anchor_promotion",
    "implementation_unblock",
    "contracts_codegen_directory_creation",
    "core_codegen_directory_creation",
    "schema_creation",
    "module_creation",
    "implementation_prompt_emission",
    "patch_application",
    "runtime_mutation",
    "canon_mutation",
    "forecast_routing",
    "github_writeback",
]

AUTHORITY_LOCKS = {
    "anchor_file_creation": False,
    "auto_approval": False,
    "canon_mutation": False,
    "canonical_source_selection": False,
    "code_generation": False,
    "code_mutation": False,
    "contracts_codegen_directory_creation": False,
    "core_codegen_directory_creation": False,
    "execution": False,
    "file_writeback": False,
    "forecast_routing": False,
    "github_writeback": False,
    "implementation_prompt_emission": False,
    "implementation_unblock": False,
    "merge_anchor_mutation": False,
    "merge_anchor_promotion": False,
    "module_creation": False,
    "notion_writeback": False,
    "operator_attestation": False,
    "operator_decision_record_creation": False,
    "patch_application": False,
    "queue_mutation": False,
    "runtime_mutation": False,
    "scheduler_mutation": False,
    "schema_creation": False,
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


def _evidence_hash(row: Mapping[str, Any]) -> str:
    stable = {
        "anchor_id": row.get("anchor_id"),
        "notion_page_id_or_url": row.get("notion_page_id_or_url"),
        "source_observed_at": row.get("source_observed_at"),
        "source_observed_title": row.get("source_observed_title"),
        "source_role": row.get("source_role"),
        "governance_posture": row.get("governance_posture"),
        "authority_boundaries": row.get("authority_boundaries"),
        "merge_rules": row.get("merge_rules"),
        "implementation_constraints": row.get("implementation_constraints"),
    }
    payload = json.dumps(stable, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _with_evidence_hashes(rows: list[dict[str, Any]], source_ready: bool) -> list[dict[str, Any]]:
    if not source_ready:
        return []
    return [{**row, "source_evidence_hash": _evidence_hash(row)} for row in rows]


def build_abx_codegen_intelligence_spine_merge_anchor_evidence_normalization_plan(
    *,
    repo_root: str | Path,
    source_merge_anchor_evidence_request_plan_path: str
    | Path = SOURCE_MERGE_ANCHOR_EVIDENCE_REQUEST_PLAN_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_merge_anchor_evidence_request_plan_path).as_posix()
    source = _read_json(root / source_merge_anchor_evidence_request_plan_path)

    source_ready = (
        source.get("artifact_type")
        == "AbxCodegenIntelligenceSpineMergeAnchorEvidenceRequestPlan.v1"
        and source.get("merge_anchor_evidence_request_plan_status")
        == EXPECTED_REQUEST_STATUS
        and source.get("recommended_next_lane") == "NOT_COMPUTABLE"
        and source.get("safe_to_auto_continue") is False
        and source.get("execution_authority") is False
        and source.get("valid_for_implementation") is False
    )
    evidence = _with_evidence_hashes(NORMALIZED_ANCHOR_EVIDENCE, source_ready)
    normalized_count = sum(
        1
        for row in evidence
        if str(row.get("normalization_status", "")).startswith("NORMALIZED_")
    )
    candidate_count = sum(
        1
        for row in evidence
        if str(row.get("normalization_status", "")).startswith("CANDIDATE_")
    )
    ambiguous_count = sum(
        1 for row in evidence if "AMBIGUOUS" in str(row.get("normalization_status", ""))
    )
    unresolved = [
        row["anchor_id"]
        for row in evidence
        if row.get("notion_page_id_or_url") == "NOT_COMPUTABLE"
        or str(row.get("normalization_status", "")).startswith("AMBIGUOUS_")
        or str(row.get("normalization_status", "")).startswith("CANDIDATE_")
    ]

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "merge_anchor_evidence_normalization_plan_status": (
            "ABX_CODEGEN_MERGE_ANCHOR_EVIDENCE_NORMALIZATION_PLAN_HELD_FOR_OPERATOR"
            if source_ready
            else "NOT_COMPUTABLE"
        ),
        "source_merge_anchor_evidence_request_plan": {
            "path": source_path,
            "hash": _sha256(root / source_merge_anchor_evidence_request_plan_path),
            "merge_anchor_evidence_request_plan_status": str(
                source.get("merge_anchor_evidence_request_plan_status", "NOT_COMPUTABLE")
            ),
            "source_ready": source_ready,
        },
        "notion_observation_scope": {
            "source": "read_only_notion_search_and_fetch_observation",
            "observed_anchor_count": len(evidence),
            "exact_page_match_count": 5 if source_ready else 0,
            "candidate_or_alias_count": 4 if source_ready else 0,
            "unresolved_anchor_count": 1 if source_ready else 0,
            "notion_writeback_performed": False,
            "live_notion_dependency_in_runner": False,
        },
        "normalized_anchor_evidence": evidence,
        "normalization_summary": {
            "requested_anchor_count": int(
                source.get("request_summary", {}).get("notion_only_anchor_count", 0)
                if isinstance(source.get("request_summary"), Mapping)
                else 0
            ),
            "observed_anchor_count": len(evidence),
            "normalized_from_exact_or_source_reference_count": normalized_count,
            "candidate_source_count": candidate_count,
            "ambiguous_or_unresolved_count": ambiguous_count,
            "operator_decision_required": True,
            "all_requested_evidence_present": False,
            "implementation_unblocked": False,
            "reason": (
                "notion_merge_anchor_evidence_is_partially_normalized_but_canonical_"
                "source_selection_and_operator_review_remain_required"
            ),
        },
        "operator_required_decisions": [
            {
                "decision": "select_canonical_prompting_upgrade_stack_source",
                "applies_to_anchor_id": "prompting_upgrade_stack_v0_1",
                "decision_status": "HELD_FOR_OPERATOR",
            },
            {
                "decision": "confirm_global_code_drop_envelope_rule_source",
                "applies_to_anchor_id": "code_drop_envelope_rule",
                "decision_status": "HELD_FOR_OPERATOR",
            },
            {
                "decision": "confirm_subsystem_merge_map_002_candidate_mapping",
                "applies_to_anchor_id": "subsystem_merge_map_002",
                "decision_status": "HELD_FOR_OPERATOR",
            },
            {
                "decision": "confirm_system_state_snapshot_alias_relationship",
                "applies_to_anchor_id": "system_state_snapshot_authoritative",
                "decision_status": "HELD_FOR_OPERATOR",
            },
            {
                "decision": "confirm_no_implementation_unblock_from_normalization",
                "applies_to_anchor_id": "all",
                "decision_status": "HELD_FOR_OPERATOR",
            },
        ],
        "blocked_actions": BLOCKED_ACTIONS,
        "recommended_next_lane": "NOT_COMPUTABLE",
        "safe_to_auto_continue": False,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "authority_locks": AUTHORITY_LOCKS,
    }
    if source_ready:
        base["normalization_summary"]["unresolved_anchor_ids"] = unresolved
    return {**base, "packet_hash": canonical_hash(base)}


def write_abx_codegen_intelligence_spine_merge_anchor_evidence_normalization_plan(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_abx_codegen_intelligence_spine_merge_anchor_evidence_normalization_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Codegen Intelligence Spine Merge Anchor Evidence Normalization Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        "- merge_anchor_evidence_normalization_plan_status: "
        f"{packet['merge_anchor_evidence_normalization_plan_status']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- execution_authority: {packet['execution_authority']}",
        f"- valid_for_implementation: {packet['valid_for_implementation']}",
        "",
        "## Normalized Anchor Evidence",
    ]
    for row in packet.get("normalized_anchor_evidence", []):
        if isinstance(row, Mapping):
            lines.append(
                f"- {row['anchor_id']}: {row['normalization_status']} "
                f"({row['notion_page_id_or_url']})"
            )
    lines.extend(["", "## Operator Required Decisions"])
    for decision in packet.get("operator_required_decisions", []):
        if isinstance(decision, Mapping):
            lines.append(
                f"- {decision['decision']}: {decision['decision_status']} "
                f"[{decision['applies_to_anchor_id']}]"
            )
    lines.extend(["", "## Blocked Actions"])
    for action in packet.get("blocked_actions", []):
        lines.append(f"- {action}")
    return lines


def write_abx_codegen_intelligence_spine_merge_anchor_evidence_normalization_plan_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(
            render_abx_codegen_intelligence_spine_merge_anchor_evidence_normalization_plan_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
