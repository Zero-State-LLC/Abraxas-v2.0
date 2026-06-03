from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Literal

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ContinuityNamespaceAliasPlan.v1"
PLAN_ID = "CONTINUITY_NAMESPACE_ALIAS_PLAN_001"
SELECTED_POLICY = "D_HYBRID_CANONICAL_GLOBAL_IDS_WITH_BRANCH_LOCAL_ALIASES"
COMPOSITE_ID_FORMAT = "<NAMESPACE_ID>.<P_LANE_ID>"
OUT_PATH = "out/continuity_namespace_alias_plan/latest.json"
READINESS_REVIEW_PATH = "out/continuity_namespace_readiness_review/latest.json"
STABILIZATION_RECEIPT_PATH = "out/continuity_namespace_stabilization_receipt/latest.json"
MIGRATION_PLAN_PATH = "out/continuity_namespace_migration_plan/latest.json"
AUDIT_PATH = "out/continuity_namespace_audit/latest.json"
CONTINUITY_SPINE_PATH = "docs/status/continuity-spine.json"
BADGES_PATH = "docs/status/badges.json"
README_PATH = "README.md"
AGENTS_PATH = "AGENTS.md"
PLANS_PATH = "PLANS.md"
REGISTRY_PATH = "core/generated_artifact_registry.py"

PlanStatus = Literal[
    "ADDITIVE_ALIAS_PLAN_EMITTED",
    "HOLD_REQUIRED",
    "NOT_COMPUTABLE",
]

_DENIED_AUTHORITY: tuple[str, ...] = (
    "authorization_authority",
    "authorization_record_creation_authority",
    "canon_promotion",
    "execution_authority",
    "forecast_influence",
    "production_activation",
    "record_creation_authority",
    "runtime_authority",
    "scheduler_mutation",
    "token_minting_authority",
)
_REQUIRED_SOURCE_PATHS: tuple[str, ...] = (
    READINESS_REVIEW_PATH,
    STABILIZATION_RECEIPT_PATH,
    MIGRATION_PLAN_PATH,
    AUDIT_PATH,
    CONTINUITY_SPINE_PATH,
    BADGES_PATH,
    README_PATH,
    AGENTS_PATH,
    PLANS_PATH,
    REGISTRY_PATH,
)
_REQUIRED_REGISTRY_OUTPUTS: tuple[str, ...] = (
    AUDIT_PATH,
    MIGRATION_PLAN_PATH,
    STABILIZATION_RECEIPT_PATH,
    READINESS_REVIEW_PATH,
    OUT_PATH,
)
_UNSAFE_ACTIONS: tuple[str, ...] = (
    "IMPLEMENT_ALIAS_MANIFEST_NOW",
    "RENAME_FILES",
    "MOVE_FILES",
    "REWRITE_EXISTING_ARTIFACTS",
    "MIGRATE_IDS",
    "MUTATE_EXISTING_SURFACES",
    "CREATE_P102H",
    "CREATE_P103",
    "CREATE_DOWNSTREAM_CONTINUITY_LANES",
    "CREATE_AUTHORIZATION_RECORDS",
    "CREATE_APPROVAL_RECORDS",
    "CREATE_DECISION_RECORDS",
    "CREATE_EXECUTION_PATHS",
    "GRANT_AUTHORIZATION",
    "MINT_TOKENS",
    "MUTATE_CANON_RUNTIME_SCHEDULER_FORECAST_STATE",
)


def _read_json(root: Path, rel_path: str) -> dict[str, Any]:
    try:
        parsed = json.loads((root / rel_path).read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _read_text(root: Path, rel_path: str) -> str:
    try:
        return (root / rel_path).read_text(encoding="utf-8")
    except (FileNotFoundError, UnicodeDecodeError):
        return ""


def _file_hash(root: Path, rel_path: str) -> str:
    try:
        return hashlib.sha256((root / rel_path).read_bytes()).hexdigest()
    except OSError:
        return "NOT_COMPUTABLE"


def _source_presence(root: Path, packets: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "path": path,
            "observed": (root / path).exists(),
            "malformed": not bool(packets.get(path, {})) if path.endswith(".json") else False,
            "sha256": _file_hash(root, path),
        }
        for path in _REQUIRED_SOURCE_PATHS
    ]


def _source_state(
    readiness_review: dict[str, Any],
    receipt: dict[str, Any],
    migration_plan: dict[str, Any],
    audit: dict[str, Any],
    spine: dict[str, Any],
    badges: dict[str, Any],
) -> dict[str, Any]:
    review_state = (
        readiness_review.get("source_state")
        if isinstance(readiness_review.get("source_state"), dict)
        else {}
    )
    receipt_state = receipt.get("source_state") if isinstance(receipt.get("source_state"), dict) else {}
    plan_state = (
        migration_plan.get("source_state")
        if isinstance(migration_plan.get("source_state"), dict)
        else {}
    )
    audit_state = audit.get("source_state") if isinstance(audit.get("source_state"), dict) else {}
    signals = badges.get("signals") if isinstance(badges.get("signals"), dict) else {}
    return {
        "canon": signals.get(
            "canon_status",
            review_state.get(
                "canon",
                receipt_state.get("canon", plan_state.get("canon", audit_state.get("canon", "NOT_COMPUTABLE"))),
            ),
        ),
        "downstream": review_state.get(
            "downstream",
            receipt_state.get(
                "downstream",
                plan_state.get("downstream", audit_state.get("downstream", "NOT_COMPUTABLE")),
            ),
        ),
        "governance": signals.get(
            "governance_status",
            review_state.get(
                "governance",
                receipt_state.get(
                    "governance",
                    plan_state.get("governance", audit_state.get("governance", "NOT_COMPUTABLE")),
                ),
            ),
        ),
        "highest_observed_lane": spine.get(
            "highest_lane",
            review_state.get(
                "highest_observed_lane",
                receipt_state.get(
                    "highest_observed_lane",
                    plan_state.get(
                        "highest_observed_lane",
                        audit_state.get("highest_observed_lane", "NOT_COMPUTABLE"),
                    ),
                ),
            ),
        ),
        "lane_count": spine.get(
            "lane_count",
            review_state.get(
                "lane_count",
                receipt_state.get(
                    "lane_count",
                    plan_state.get("lane_count", audit_state.get("lane_count", "NOT_COMPUTABLE")),
                ),
            ),
        ),
    }


def _source_state_matches(source_state: dict[str, Any]) -> bool:
    return source_state == {
        "canon": "ADVISORY_ONLY",
        "downstream": "NOT_COMPUTABLE",
        "governance": "FROZEN",
        "highest_observed_lane": "P102G",
        "lane_count": 58,
    }


def _registry_binding(root: Path) -> dict[str, Any]:
    registry_text = _read_text(root, REGISTRY_PATH)
    rows = [
        {"artifact_path": path, "registered": path in registry_text}
        for path in _REQUIRED_REGISTRY_OUTPUTS
    ]
    return {
        "checked_paths": rows,
        "registry_path": REGISTRY_PATH,
        "status": "BOUND" if all(row["registered"] for row in rows) else "NOT_COMPUTABLE",
    }


def _all_authority_locks_false(packet: dict[str, Any]) -> bool:
    locks = packet.get("authority_locks") if isinstance(packet.get("authority_locks"), dict) else {}
    return all(locks.get(name) is False for name in _DENIED_AUTHORITY)


def _readiness_review_qualifies(readiness_review: dict[str, Any]) -> bool:
    return (
        readiness_review.get("review_id") == "CONTINUITY_NAMESPACE_READINESS_REVIEW_001"
        and readiness_review.get("readiness_status") == "READY_FOR_ADDITIVE_ALIAS_PLAN"
        and readiness_review.get("safe_next_surface_recommendation")
        == "CONTINUITY_NAMESPACE_ADDITIVE_ALIAS_PLAN_001_ADVISORY_ONLY"
        and readiness_review.get("advisory_only") is True
        and readiness_review.get("valid_for_execution") is False
        and readiness_review.get("recommended_next_lane") == "NOT_COMPUTABLE"
        and _all_authority_locks_false(readiness_review)
    )


def _prior_surfaces_non_executable(
    audit: dict[str, Any],
    migration_plan: dict[str, Any],
    receipt: dict[str, Any],
) -> bool:
    return all(
        packet.get("advisory_only") is True
        and packet.get("valid_for_execution") is False
        and packet.get("recommended_next_lane") == "NOT_COMPUTABLE"
        and _all_authority_locks_false(packet)
        for packet in (audit, migration_plan, receipt)
    )


def _plan_checks(
    *,
    source_inputs: list[dict[str, Any]],
    source_state: dict[str, Any],
    registry_binding: dict[str, Any],
    readiness_review: dict[str, Any],
    audit: dict[str, Any],
    migration_plan: dict[str, Any],
    receipt: dict[str, Any],
) -> dict[str, bool]:
    return {
        "all_required_sources_observed": all(row["observed"] for row in source_inputs),
        "all_required_json_sources_well_formed": not any(row["malformed"] for row in source_inputs),
        "readiness_review_authorizes_plan_only": _readiness_review_qualifies(readiness_review),
        "registry_binding_bound": registry_binding.get("status") == "BOUND",
        "source_state_constants_match": _source_state_matches(source_state),
        "prior_surfaces_non_executable": _prior_surfaces_non_executable(audit, migration_plan, receipt),
        "selected_policy_matches": readiness_review.get("selected_policy")
        == migration_plan.get("selected_policy")
        == receipt.get("selected_policy")
        == SELECTED_POLICY,
        "composite_id_format_selected": readiness_review.get("composite_id_format") == COMPOSITE_ID_FORMAT,
    }


def _plan_status(checks: dict[str, bool]) -> PlanStatus:
    source_keys = {
        "all_required_sources_observed",
        "all_required_json_sources_well_formed",
        "registry_binding_bound",
    }
    if not all(checks[key] for key in source_keys):
        return "NOT_COMPUTABLE"
    if all(checks.values()):
        return "ADDITIVE_ALIAS_PLAN_EMITTED"
    return "HOLD_REQUIRED"


def _plan_blockers(status: PlanStatus, checks: dict[str, bool]) -> list[dict[str, str]]:
    if status == "ADDITIVE_ALIAS_PLAN_EMITTED":
        return []
    return [
        {
            "blocker_id": key.upper(),
            "status": "FAILED",
            "reason": "Required alias-plan predicate was not satisfied.",
        }
        for key, value in sorted(checks.items())
        if value is False
    ]


def build_continuity_namespace_alias_plan(repo_root: Path | str | None = None) -> dict[str, Any]:
    root = Path(repo_root) if repo_root is not None else Path.cwd()
    readiness_review = _read_json(root, READINESS_REVIEW_PATH)
    receipt = _read_json(root, STABILIZATION_RECEIPT_PATH)
    migration_plan = _read_json(root, MIGRATION_PLAN_PATH)
    audit = _read_json(root, AUDIT_PATH)
    spine = _read_json(root, CONTINUITY_SPINE_PATH)
    badges = _read_json(root, BADGES_PATH)
    packets = {
        READINESS_REVIEW_PATH: readiness_review,
        STABILIZATION_RECEIPT_PATH: receipt,
        MIGRATION_PLAN_PATH: migration_plan,
        AUDIT_PATH: audit,
        CONTINUITY_SPINE_PATH: spine,
        BADGES_PATH: badges,
    }
    source_inputs = _source_presence(root, packets)
    source_state = _source_state(readiness_review, receipt, migration_plan, audit, spine, badges)
    registry_binding = _registry_binding(root)
    checks = _plan_checks(
        source_inputs=source_inputs,
        source_state=source_state,
        registry_binding=registry_binding,
        readiness_review=readiness_review,
        audit=audit,
        migration_plan=migration_plan,
        receipt=receipt,
    )
    status = _plan_status(checks)

    packet: dict[str, Any] = {
        "additive_metadata_strategy": {
            "allowed_additions": [
                "alias_manifest_artifact",
                "status_surface_alias_metadata_fields",
                "validation_receipt_references",
            ],
            "metadata_posture": "ADDITIVE_ONLY_NO_EXISTING_SURFACE_MUTATION_IN_THIS_PLAN",
            "required_field_stability": "existing_generated_artifact_fields_remain_byte_stable_until_separate_implementation_authorization",
        },
        "advisory_only": True,
        "alias_collision_handling": {
            "collision_policy": "FAIL_CLOSED_NOT_COMPUTABLE",
            "required_checks": [
                "canonical_id_uniqueness",
                "alias_id_uniqueness",
                "legacy_id_to_canonical_id_single_binding",
                "namespace_prefix_uniqueness",
            ],
            "tie_breaking": "NO_AUTOMATED_TIE_BREAKING_OPERATOR_REVIEW_REQUIRED",
        },
        "alias_lookup_precedence": [
            "canonical_global_id_exact_match",
            "canonical_composite_id_exact_match",
            "namespace_scoped_alias_exact_match",
            "legacy_branch_local_alias_exact_match_when_unambiguous",
            "fail_closed_on_missing_or_ambiguous_alias",
        ],
        "alias_manifest_shape": {
            "artifact_path": "out/continuity_namespace_alias_manifest/latest.json",
            "planned_only": True,
            "required_top_level_fields": [
                "advisory_only",
                "alias_manifest_id",
                "artifact_type",
                "authority_locks",
                "canonical_namespace_policy",
                "generated_from_plan_id",
                "manifest_entries",
                "packet_hash",
                "valid_for_execution",
            ],
            "manifest_entry_shape": {
                "alias_id": "string",
                "alias_scope": "namespace_or_branch",
                "canonical_composite_id": COMPOSITE_ID_FORMAT,
                "canonical_global_id": "P<number>",
                "legacy_id": "string_or_null",
                "namespace_id": "string",
                "source_artifact_path": "repo_relative_path",
            },
        },
        "artifact_type": ARTIFACT_TYPE,
        "authority_locks": {name: False for name in _DENIED_AUTHORITY},
        "authorization_authority": False,
        "authorization_granted": False,
        "authorization_record_created": False,
        "authorization_record_creation_authority": False,
        "canon_promotion": False,
        "compatibility_with_existing_generated_artifacts": {
            "compatible": True,
            "compatibility_posture": "PLAN_ONLY_ADDITIVE_METADATA_NO_PATH_OR_ID_REWRITE",
            "generated_artifact_registry_binding_required": True,
            "legacy_artifact_paths_preserved": True,
        },
        "composite_id_format": COMPOSITE_ID_FORMAT,
        "consumed_audit_artifact_path": AUDIT_PATH,
        "consumed_migration_plan_artifact_path": MIGRATION_PLAN_PATH,
        "consumed_readiness_review_artifact_path": READINESS_REVIEW_PATH,
        "consumed_stabilization_receipt_artifact_path": STABILIZATION_RECEIPT_PATH,
        "denied_authority": list(_DENIED_AUTHORITY),
        "execution_authority": False,
        "forecast_influence": False,
        "legacy_id_rewrite_rule": "FORBIDDEN",
        "no_path_rename_rule": "FORBIDDEN",
        "packet_source_inputs": source_inputs,
        "plan_blockers": _plan_blockers(status, checks),
        "plan_checks": checks,
        "plan_id": PLAN_ID,
        "plan_status": status,
        "production_activation": False,
        "projection_only": True,
        "recommended_next_action": "HOLD_FOR_STABILIZATION_RECEIPT_BEFORE_IMPLEMENTATION",
        "recommended_next_lane": "NOT_COMPUTABLE",
        "record_creation_authority": False,
        "registry_binding": registry_binding,
        "required_evidence_for_activation": [
            "future_stabilization_receipt_over_alias_plan",
            "separate_operator_authorization_for_alias_manifest_implementation",
            "validation_gate_receipts_after_additive_manifest_draft",
            "no_change_to_P102G_lane_count_58_without_separate_authorization",
        ],
        "runtime_authority": False,
        "scheduler_mutation": False,
        "selected_policy": SELECTED_POLICY,
        "source_state": source_state,
        "stabilization_receipt_requirement_before_implementation": {
            "required": True,
            "required_status": "ALIAS_PLAN_STABILIZED_ADVISORY_ONLY",
            "valid_for_implementation_until_receipt": False,
        },
        "status_surface_additive_fields": [
            "alias_manifest_artifact_path",
            "alias_manifest_status",
            "alias_collision_status",
            "alias_lookup_policy",
            "alias_plan_stabilization_receipt_path",
        ],
        "token_minting_allowed": False,
        "token_minting_authority": False,
        "unsafe_actions": list(_UNSAFE_ACTIONS),
        "valid_for_execution": False,
        "validation_gates": [
            "schema_validation",
            "canonical_hash_validation",
            "registry_binding_validation",
            "no_path_rename_validation",
            "no_legacy_id_rewrite_validation",
            "alias_collision_validation",
            "authority_lock_validation",
            "stabilization_receipt_validation_before_implementation",
        ],
    }
    packet["packet_hash"] = canonical_hash(packet)
    return packet


def write_continuity_namespace_alias_plan(path: Path | str, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
