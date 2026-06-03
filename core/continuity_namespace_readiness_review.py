from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Literal

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ContinuityNamespaceReadinessReview.v1"
REVIEW_ID = "CONTINUITY_NAMESPACE_READINESS_REVIEW_001"
SELECTED_POLICY = "D_HYBRID_CANONICAL_GLOBAL_IDS_WITH_BRANCH_LOCAL_ALIASES"
COMPOSITE_ID_FORMAT = "<NAMESPACE_ID>.<P_LANE_ID>"
OUT_PATH = "out/continuity_namespace_readiness_review/latest.json"
AUDIT_PATH = "out/continuity_namespace_audit/latest.json"
MIGRATION_PLAN_PATH = "out/continuity_namespace_migration_plan/latest.json"
STABILIZATION_RECEIPT_PATH = "out/continuity_namespace_stabilization_receipt/latest.json"
CONTINUITY_SPINE_PATH = "docs/status/continuity-spine.json"
BADGES_PATH = "docs/status/badges.json"
REGISTRY_PATH = "core/generated_artifact_registry.py"

ReadinessStatus = Literal[
    "READY_FOR_ADDITIVE_ALIAS_PLAN",
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
_UNSAFE_ACTIONS: tuple[str, ...] = (
    "RENAME_FILES",
    "MOVE_FILES",
    "REWRITE_EXISTING_ARTIFACTS",
    "MIGRATE_IDS",
    "ADD_COMPOSITE_IDS_INTO_EXISTING_SURFACES",
    "CREATE_ALIAS_MANIFESTS_NOW",
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
_REQUIRED_SOURCE_PATHS: tuple[str, ...] = (
    AUDIT_PATH,
    MIGRATION_PLAN_PATH,
    STABILIZATION_RECEIPT_PATH,
    CONTINUITY_SPINE_PATH,
    BADGES_PATH,
    REGISTRY_PATH,
)
_REQUIRED_REGISTRY_OUTPUTS: tuple[str, ...] = (
    AUDIT_PATH,
    MIGRATION_PLAN_PATH,
    STABILIZATION_RECEIPT_PATH,
    OUT_PATH,
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
    audit: dict[str, Any],
    migration_plan: dict[str, Any],
    receipt: dict[str, Any],
    spine: dict[str, Any],
    badges: dict[str, Any],
) -> dict[str, Any]:
    audit_state = audit.get("source_state") if isinstance(audit.get("source_state"), dict) else {}
    plan_state = (
        migration_plan.get("source_state")
        if isinstance(migration_plan.get("source_state"), dict)
        else {}
    )
    receipt_state = receipt.get("source_state") if isinstance(receipt.get("source_state"), dict) else {}
    signals = badges.get("signals") if isinstance(badges.get("signals"), dict) else {}
    return {
        "canon": signals.get(
            "canon_status",
            receipt_state.get("canon", plan_state.get("canon", audit_state.get("canon", "NOT_COMPUTABLE"))),
        ),
        "downstream": receipt_state.get(
            "downstream",
            plan_state.get("downstream", audit_state.get("downstream", "NOT_COMPUTABLE")),
        ),
        "governance": signals.get(
            "governance_status",
            receipt_state.get(
                "governance",
                plan_state.get("governance", audit_state.get("governance", "NOT_COMPUTABLE")),
            ),
        ),
        "highest_observed_lane": spine.get(
            "highest_lane",
            receipt_state.get(
                "highest_observed_lane",
                plan_state.get(
                    "highest_observed_lane",
                    audit_state.get("highest_observed_lane", "NOT_COMPUTABLE"),
                ),
            ),
        ),
        "lane_count": spine.get(
            "lane_count",
            receipt_state.get(
                "lane_count",
                plan_state.get("lane_count", audit_state.get("lane_count", "NOT_COMPUTABLE")),
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


def _audit_policy(audit: dict[str, Any]) -> str:
    recommendation = audit.get("namespace_policy_recommendation")
    if isinstance(recommendation, dict) and isinstance(recommendation.get("recommended_policy"), str):
        return recommendation["recommended_policy"]
    return "NOT_COMPUTABLE"


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


def _unresolved_collision_summary(audit: dict[str, Any]) -> dict[str, Any]:
    collisions = audit.get("collisions") if isinstance(audit.get("collisions"), list) else []
    critical = [
        row.get("p_number")
        for row in collisions
        if isinstance(row, dict) and row.get("p_number") in {"P103", "P104", "P105", "P106", "P107"}
    ]
    return {
        "critical_ambiguity": "P103_TO_P107_RESEARCH_BRANCH_NAME_COLLISION",
        "critical_p_numbers": sorted(set(critical)),
        "resolution_posture": "CONTAINED_BY_STABILIZATION_RECEIPT_NOT_IMPLEMENTED",
        "total_collision_count": len(collisions),
    }


def _unresolved_orphan_summary(audit: dict[str, Any]) -> dict[str, Any]:
    orphaned = audit.get("orphaned_references") if isinstance(audit.get("orphaned_references"), list) else []
    return {
        "resolution_posture": "MUST_REMAIN_REVIEW_INPUT_FOR_FUTURE_ALIAS_PLAN",
        "total_orphaned_recommended_next_lane_references": len(orphaned),
    }


def _all_authority_locks_false(packet: dict[str, Any]) -> bool:
    locks = packet.get("authority_locks") if isinstance(packet.get("authority_locks"), dict) else {}
    return all(locks.get(name) is False for name in _DENIED_AUTHORITY)


def _readiness_checks(
    *,
    audit: dict[str, Any],
    migration_plan: dict[str, Any],
    receipt: dict[str, Any],
    source_inputs: list[dict[str, Any]],
    source_state: dict[str, Any],
    registry_binding: dict[str, Any],
    safe_next_surface_recommendation: str,
) -> dict[str, bool]:
    return {
        "all_required_sources_observed": all(row["observed"] for row in source_inputs),
        "all_required_json_sources_well_formed": not any(row["malformed"] for row in source_inputs),
        "audit_plan_consistency_consistent": receipt.get("audit_plan_consistency_status") == "CONSISTENT",
        "registry_binding_bound": registry_binding.get("status") == "BOUND",
        "blocked_actions_denied": receipt.get("blocked_action_status") == "BLOCKED_ACTIONS_REMAIN_DENIED",
        "source_state_constants_match": _source_state_matches(source_state),
        "audit_non_executable": audit.get("advisory_only") is True
        and audit.get("valid_for_execution") is False
        and audit.get("recommended_next_lane") == "NOT_COMPUTABLE"
        and _all_authority_locks_false(audit),
        "migration_plan_non_executable": migration_plan.get("advisory_only") is True
        and migration_plan.get("valid_for_execution") is False
        and migration_plan.get("recommended_next_lane") == "NOT_COMPUTABLE"
        and _all_authority_locks_false(migration_plan),
        "receipt_non_executable": receipt.get("advisory_only") is True
        and receipt.get("valid_for_execution") is False
        and receipt.get("recommended_next_lane") == "NOT_COMPUTABLE"
        and _all_authority_locks_false(receipt),
        "selected_policy_matches": _audit_policy(audit)
        == migration_plan.get("selected_policy")
        == receipt.get("selected_policy")
        == SELECTED_POLICY,
        "composite_id_format_selected": receipt.get("composite_id_format") == COMPOSITE_ID_FORMAT,
        "no_composite_id_mutation_yet": receipt.get("composite_id_mutation_status")
        == "NO_COMPOSITE_ID_MUTATION_DETECTED",
        "safe_next_surface_is_plan_only": safe_next_surface_recommendation
        == "CONTINUITY_NAMESPACE_ADDITIVE_ALIAS_PLAN_001_ADVISORY_ONLY",
    }


def _readiness_status(checks: dict[str, bool]) -> ReadinessStatus:
    source_keys = {
        "all_required_sources_observed",
        "all_required_json_sources_well_formed",
    }
    if not all(checks[key] for key in source_keys):
        return "NOT_COMPUTABLE"
    if all(checks.values()):
        return "READY_FOR_ADDITIVE_ALIAS_PLAN"
    return "HOLD_REQUIRED"


def _readiness_blockers(status: ReadinessStatus, checks: dict[str, bool]) -> list[dict[str, str]]:
    if status == "READY_FOR_ADDITIVE_ALIAS_PLAN":
        return []
    return [
        {
            "blocker_id": key.upper(),
            "status": "FAILED",
            "reason": "Required readiness predicate was not satisfied.",
        }
        for key, value in sorted(checks.items())
        if value is False
    ]


def build_continuity_namespace_readiness_review(
    repo_root: Path | str | None = None,
) -> dict[str, Any]:
    root = Path(repo_root) if repo_root is not None else Path.cwd()
    audit = _read_json(root, AUDIT_PATH)
    migration_plan = _read_json(root, MIGRATION_PLAN_PATH)
    receipt = _read_json(root, STABILIZATION_RECEIPT_PATH)
    spine = _read_json(root, CONTINUITY_SPINE_PATH)
    badges = _read_json(root, BADGES_PATH)
    packets = {
        AUDIT_PATH: audit,
        MIGRATION_PLAN_PATH: migration_plan,
        STABILIZATION_RECEIPT_PATH: receipt,
        CONTINUITY_SPINE_PATH: spine,
        BADGES_PATH: badges,
    }
    source_inputs = _source_presence(root, packets)
    source_state = _source_state(audit, migration_plan, receipt, spine, badges)
    registry_binding = _registry_binding(root)
    safe_next_surface_recommendation = "CONTINUITY_NAMESPACE_ADDITIVE_ALIAS_PLAN_001_ADVISORY_ONLY"
    checks = _readiness_checks(
        audit=audit,
        migration_plan=migration_plan,
        receipt=receipt,
        source_inputs=source_inputs,
        source_state=source_state,
        registry_binding=registry_binding,
        safe_next_surface_recommendation=safe_next_surface_recommendation,
    )
    status = _readiness_status(checks)

    packet: dict[str, Any] = {
        "advisory_only": True,
        "artifact_type": ARTIFACT_TYPE,
        "authority_locks": {name: False for name in _DENIED_AUTHORITY},
        "authorization_authority": False,
        "authorization_granted": False,
        "authorization_record_created": False,
        "authorization_record_creation_authority": False,
        "canon_promotion": False,
        "composite_id_format": COMPOSITE_ID_FORMAT,
        "consumed_audit_artifact_path": AUDIT_PATH,
        "consumed_migration_plan_artifact_path": MIGRATION_PLAN_PATH,
        "consumed_stabilization_receipt_artifact_path": STABILIZATION_RECEIPT_PATH,
        "denied_authority": list(_DENIED_AUTHORITY),
        "execution_authority": False,
        "forecast_influence": False,
        "packet_source_inputs": source_inputs,
        "production_activation": False,
        "projection_only": True,
        "readiness_blockers": _readiness_blockers(status, checks),
        "readiness_checks": checks,
        "readiness_status": status,
        "recommended_next_action": "DRAFT_ADVISORY_ONLY_ADDITIVE_ALIAS_PLAN" if status == "READY_FOR_ADDITIVE_ALIAS_PLAN" else "HOLD_FOR_NAMESPACE_READINESS_REVIEW_REPAIR",
        "recommended_next_lane": "NOT_COMPUTABLE",
        "record_creation_authority": False,
        "registry_binding": registry_binding,
        "required_evidence_for_activation": [
            "explicit_future_operator_authorization_record",
            "separate_governance_design_for_alias_implementation",
            "validation_receipts_after_additive_alias_plan",
            "no_change_to_P102G_lane_count_58_without_separate_authorization",
        ],
        "review_id": REVIEW_ID,
        "runtime_authority": False,
        "safe_next_surface_recommendation": safe_next_surface_recommendation,
        "scheduler_mutation": False,
        "selected_policy": SELECTED_POLICY,
        "source_state": source_state,
        "token_minting_allowed": False,
        "token_minting_authority": False,
        "unsafe_actions": list(_UNSAFE_ACTIONS),
        "unresolved_collision_summary": _unresolved_collision_summary(audit),
        "unresolved_orphan_summary": _unresolved_orphan_summary(audit),
        "valid_for_execution": False,
    }
    packet["packet_hash"] = canonical_hash(packet)
    return packet


def write_continuity_namespace_readiness_review(
    path: Path | str,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
