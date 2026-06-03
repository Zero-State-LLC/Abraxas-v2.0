from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ContinuityNamespaceStabilizationReceipt.v1"
RECEIPT_ID = "CONTINUITY_NAMESPACE_STABILIZATION_RECEIPT_001"
SELECTED_POLICY = "D_HYBRID_CANONICAL_GLOBAL_IDS_WITH_BRANCH_LOCAL_ALIASES"
COMPOSITE_ID_FORMAT = "<NAMESPACE_ID>.<P_LANE_ID>"
OUT_PATH = "out/continuity_namespace_stabilization_receipt/latest.json"
AUDIT_PATH = "out/continuity_namespace_audit/latest.json"
MIGRATION_PLAN_PATH = "out/continuity_namespace_migration_plan/latest.json"
CONTINUITY_SPINE_PATH = "docs/status/continuity-spine.json"
BADGES_PATH = "docs/status/badges.json"
REGISTRY_PATH = "core/generated_artifact_registry.py"

_COMPOSITE_ID_RE = re.compile(r"\b[A-Z][A-Z0-9_]+\.P\d{1,3}[A-Z]?\b")
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
_BLOCKED_ACTIONS: tuple[str, ...] = (
    "RENAME_FILES",
    "MOVE_FILES",
    "REWRITE_EXISTING_ARTIFACTS",
    "MIGRATE_IDS",
    "ADD_COMPOSITE_IDS_TO_EXISTING_SURFACES",
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
_REQUIRED_REGISTRY_OUTPUTS: tuple[str, ...] = (
    AUDIT_PATH,
    MIGRATION_PLAN_PATH,
    OUT_PATH,
)
_REQUIRED_SOURCE_PATHS: tuple[str, ...] = (
    AUDIT_PATH,
    MIGRATION_PLAN_PATH,
    CONTINUITY_SPINE_PATH,
    BADGES_PATH,
    REGISTRY_PATH,
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


def _packet_hash_status(packet: dict[str, Any]) -> dict[str, Any]:
    observed = packet.get("packet_hash")
    if not isinstance(observed, str):
        return {
            "computed_hash": "NOT_COMPUTABLE",
            "hash_match": False,
            "observed_hash": "NOT_COMPUTABLE",
        }
    without_hash = dict(packet)
    without_hash.pop("packet_hash", None)
    computed = canonical_hash(without_hash)
    return {
        "computed_hash": computed,
        "hash_match": computed == observed,
        "observed_hash": observed,
    }


def _source_state(
    audit: dict[str, Any],
    migration_plan: dict[str, Any],
    spine: dict[str, Any],
    badges: dict[str, Any],
) -> dict[str, Any]:
    audit_state = audit.get("source_state") if isinstance(audit.get("source_state"), dict) else {}
    plan_state = (
        migration_plan.get("source_state")
        if isinstance(migration_plan.get("source_state"), dict)
        else {}
    )
    signals = badges.get("signals") if isinstance(badges.get("signals"), dict) else {}
    return {
        "canon": signals.get(
            "canon_status",
            plan_state.get("canon", audit_state.get("canon", "NOT_COMPUTABLE")),
        ),
        "downstream": plan_state.get(
            "downstream",
            audit_state.get("downstream", migration_plan.get("recommended_next_lane", "NOT_COMPUTABLE")),
        ),
        "governance": signals.get(
            "governance_status",
            plan_state.get("governance", audit_state.get("governance", "NOT_COMPUTABLE")),
        ),
        "highest_observed_lane": spine.get(
            "highest_lane",
            plan_state.get("highest_observed_lane", audit_state.get("highest_observed_lane", "NOT_COMPUTABLE")),
        ),
        "lane_count": spine.get(
            "lane_count",
            plan_state.get("lane_count", audit_state.get("lane_count", "NOT_COMPUTABLE")),
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


def _non_execution_boundary(audit: dict[str, Any], migration_plan: dict[str, Any]) -> dict[str, Any]:
    audit_locks = audit.get("authority_locks") if isinstance(audit.get("authority_locks"), dict) else {}
    plan_locks = (
        migration_plan.get("authority_locks")
        if isinstance(migration_plan.get("authority_locks"), dict)
        else {}
    )
    checks = {
        "audit_advisory_only": audit.get("advisory_only") is True,
        "audit_valid_for_execution_false": audit.get("valid_for_execution") is False,
        "audit_recommended_next_lane_not_computable": audit.get("recommended_next_lane") == "NOT_COMPUTABLE",
        "audit_authority_locks_false": all(audit_locks.get(name) is False for name in _DENIED_AUTHORITY),
        "plan_advisory_only": migration_plan.get("advisory_only") is True,
        "plan_valid_for_execution_false": migration_plan.get("valid_for_execution") is False,
        "plan_recommended_next_lane_not_computable": migration_plan.get("recommended_next_lane") == "NOT_COMPUTABLE",
        "plan_authority_locks_false": all(plan_locks.get(name) is False for name in _DENIED_AUTHORITY),
    }
    return {
        "checks": checks,
        "status": "NON_EXECUTION_BOUNDARY_CONFIRMED" if all(checks.values()) else "NOT_COMPUTABLE",
    }


def _blocked_action_status(migration_plan: dict[str, Any]) -> dict[str, Any]:
    explicit_boundary = (
        migration_plan.get("explicit_non_execution_boundary")
        if isinstance(migration_plan.get("explicit_non_execution_boundary"), dict)
        else {}
    )
    plan_blocked_actions = migration_plan.get("blocked_actions")
    blocked_set = set(plan_blocked_actions) if isinstance(plan_blocked_actions, list) else set()
    checks = {
        "route_authority_false": explicit_boundary.get("route_authority") is False,
        "mutation_authority_false": explicit_boundary.get("mutation_authority") is False,
        "valid_for_execution_false": explicit_boundary.get("valid_for_execution") is False,
        "create_p102h_blocked": "CREATE_P102H" in blocked_set,
        "create_p103_temporal_route_blocked": "CREATE_P103_TEMPORAL_OPERATOR_ROUTE" in blocked_set,
        "id_migration_blocked": "MIGRATE_IDS_WITHOUT_SEPARATE_AUTHORIZATION" in blocked_set,
    }
    return {
        "blocked_actions": list(_BLOCKED_ACTIONS),
        "checks": checks,
        "status": "BLOCKED_ACTIONS_REMAIN_DENIED" if all(checks.values()) else "NOT_COMPUTABLE",
    }


def _byte_stability(audit: dict[str, Any], migration_plan: dict[str, Any], root: Path) -> dict[str, Any]:
    audit_hash_status = _packet_hash_status(audit)
    plan_hash_status = _packet_hash_status(migration_plan)
    checks = {
        "audit_packet_hash_match": audit_hash_status["hash_match"],
        "migration_plan_packet_hash_match": plan_hash_status["hash_match"],
        "audit_file_observed": _file_hash(root, AUDIT_PATH) != "NOT_COMPUTABLE",
        "migration_plan_file_observed": _file_hash(root, MIGRATION_PLAN_PATH) != "NOT_COMPUTABLE",
    }
    return {
        "artifact_hashes": {
            AUDIT_PATH: _file_hash(root, AUDIT_PATH),
            MIGRATION_PLAN_PATH: _file_hash(root, MIGRATION_PLAN_PATH),
        },
        "packet_hash_checks": {
            "audit": audit_hash_status,
            "migration_plan": plan_hash_status,
        },
        "status": "BYTE_STABLE" if all(checks.values()) else "NOT_COMPUTABLE",
    }


def _audit_plan_consistency(
    audit: dict[str, Any],
    migration_plan: dict[str, Any],
    source_state: dict[str, Any],
) -> dict[str, Any]:
    audit_path_rows = migration_plan.get("packet_source_inputs")
    consumes_audit = False
    if isinstance(audit_path_rows, list):
        consumes_audit = any(
            isinstance(row, dict)
            and row.get("path") == AUDIT_PATH
            and row.get("observed") is True
            for row in audit_path_rows
        )
    checks = {
        "migration_plan_consumes_audit": consumes_audit,
        "source_audit_id_matches": migration_plan.get("source_audit_id") == audit.get("audit_id") == "CONTINUITY_NAMESPACE_AUDIT_001",
        "selected_policy_matches": _audit_policy(audit) == migration_plan.get("selected_policy") == SELECTED_POLICY,
        "source_audit_policy_matches": migration_plan.get("source_audit_policy") == SELECTED_POLICY,
        "source_state_constants_match": _source_state_matches(source_state),
        "critical_ambiguity_contained": any(
            isinstance(row, dict)
            and row.get("ambiguity") == "P103_TO_P107_RESEARCH_BRANCH_NAME_COLLISION"
            for row in migration_plan.get("critical_ambiguities", [])
            if isinstance(migration_plan.get("critical_ambiguities"), list)
        ),
    }
    return {
        "checks": checks,
        "status": "CONSISTENT" if all(checks.values()) else "NOT_COMPUTABLE",
    }


def _composite_mutation_status(root: Path) -> dict[str, Any]:
    checked_paths = (CONTINUITY_SPINE_PATH, BADGES_PATH, REGISTRY_PATH)
    hits = []
    for path in checked_paths:
        matches = sorted(set(_COMPOSITE_ID_RE.findall(_read_text(root, path))))
        if matches:
            hits.append({"path": path, "matches": matches})
    return {
        "checked_paths": list(checked_paths),
        "composite_id_mutation_detected": bool(hits),
        "hits": hits,
        "status": "NO_COMPOSITE_ID_MUTATION_DETECTED" if not hits else "NOT_COMPUTABLE",
    }


def _stabilization_window_status(migration_plan: dict[str, Any]) -> dict[str, Any]:
    window = (
        migration_plan.get("stabilization_window")
        if isinstance(migration_plan.get("stabilization_window"), dict)
        else {}
    )
    checks = {
        "required_true": window.get("required") is True,
        "minimum_validation_passes_three": window.get("minimum_validation_passes") == 3,
        "drift_allowed_false": window.get("drift_allowed") is False,
        "authority_escalation_allowed_false": window.get("authority_escalation_allowed") is False,
    }
    return {
        "checks": checks,
        "status": "STABILIZATION_HOLD_READY" if all(checks.values()) else "NOT_COMPUTABLE",
    }


def _source_inputs(root: Path) -> list[dict[str, Any]]:
    return [
        {"path": path, "observed": (root / path).exists(), "sha256": _file_hash(root, path)}
        for path in _REQUIRED_SOURCE_PATHS
    ]


def build_continuity_namespace_stabilization_receipt(
    repo_root: Path | str | None = None,
) -> dict[str, Any]:
    root = Path(repo_root) if repo_root is not None else Path.cwd()
    audit = _read_json(root, AUDIT_PATH)
    migration_plan = _read_json(root, MIGRATION_PLAN_PATH)
    spine = _read_json(root, CONTINUITY_SPINE_PATH)
    badges = _read_json(root, BADGES_PATH)
    source_state = _source_state(audit, migration_plan, spine, badges)
    audit_plan_consistency = _audit_plan_consistency(audit, migration_plan, source_state)
    registry_binding = _registry_binding(root)
    byte_stability = _byte_stability(audit, migration_plan, root)
    non_execution_boundary = _non_execution_boundary(audit, migration_plan)
    blocked_actions = _blocked_action_status(migration_plan)
    stabilization_window = _stabilization_window_status(migration_plan)
    composite_mutation = _composite_mutation_status(root)

    packet: dict[str, Any] = {
        "advisory_only": True,
        "artifact_type": ARTIFACT_TYPE,
        "audit_plan_consistency": audit_plan_consistency,
        "audit_plan_consistency_status": audit_plan_consistency["status"],
        "authority_locks": {name: False for name in _DENIED_AUTHORITY},
        "authorization_authority": False,
        "authorization_granted": False,
        "authorization_record_created": False,
        "authorization_record_creation_authority": False,
        "blocked_action_status": blocked_actions["status"],
        "blocked_actions": blocked_actions,
        "byte_stability": byte_stability,
        "byte_stability_status": byte_stability["status"],
        "canon_promotion": False,
        "composite_id_format": COMPOSITE_ID_FORMAT,
        "composite_id_mutation_status": composite_mutation["status"],
        "composite_id_mutation_verification": composite_mutation,
        "consumed_audit_artifact_path": AUDIT_PATH,
        "consumed_migration_plan_artifact_path": MIGRATION_PLAN_PATH,
        "denied_authority": list(_DENIED_AUTHORITY),
        "execution_authority": False,
        "forecast_influence": False,
        "non_execution_boundary": non_execution_boundary,
        "non_execution_boundary_status": non_execution_boundary["status"],
        "packet_source_inputs": _source_inputs(root),
        "production_activation": False,
        "projection_only": True,
        "receipt_id": RECEIPT_ID,
        "recommended_next_action": "HOLD_NAMESPACE_MIGRATION_UNTIL_FUTURE_ADVISORY_IMPLEMENTATION_AUTHORIZATION_DESIGN",
        "recommended_next_lane": "NOT_COMPUTABLE",
        "record_creation_authority": False,
        "registry_binding": registry_binding,
        "registry_binding_status": registry_binding["status"],
        "runtime_authority": False,
        "scheduler_mutation": False,
        "selected_policy": SELECTED_POLICY,
        "source_state": source_state,
        "stabilization_window": stabilization_window,
        "stabilization_window_status": stabilization_window["status"],
        "token_minting_allowed": False,
        "token_minting_authority": False,
        "valid_for_execution": False,
    }
    packet["packet_hash"] = canonical_hash(packet)
    return packet


def write_continuity_namespace_stabilization_receipt(
    path: Path | str,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
