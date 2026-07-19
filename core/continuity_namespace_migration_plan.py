from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ContinuityNamespaceMigrationPlan.v1"
PLAN_ID = "CONTINUITY_NAMESPACE_MIGRATION_PLAN_001"
SELECTED_POLICY = "D_HYBRID_CANONICAL_GLOBAL_IDS_WITH_BRANCH_LOCAL_ALIASES"
OUT_PATH = "out/continuity_namespace_migration_plan/latest.json"
SOURCE_AUDIT_PATH = "out/continuity_namespace_audit/latest.json"
CONTINUITY_SPINE_PATH = "docs/status/continuity-spine.json"
BADGES_PATH = "docs/status/badges.json"
README_PATH = "README.md"
AGENTS_PATH = "AGENTS.md"
PLANS_PATH = "PLANS.md"
REGISTRY_PATH = "core/generated_artifact_registry.py"

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
    "CREATE_P102H",
    "CREATE_P103_TEMPORAL_OPERATOR_ROUTE",
    "CREATE_DOWNSTREAM_CONTINUITY_LANE",
    "CREATE_AUTHORIZATION_RECORDS",
    "CREATE_APPROVAL_RECORDS",
    "CREATE_DECISION_RECORDS",
    "CREATE_EXECUTION_PATHS",
    "GRANT_AUTHORIZATION",
    "MINT_TOKENS",
    "MUTATE_CANON_RUNTIME_SCHEDULER_FORECAST_STATE",
    "RENAME_FILES",
    "MOVE_FILES",
    "MIGRATE_IDS_WITHOUT_SEPARATE_AUTHORIZATION",
)

_COMPOSITE_ID_EXAMPLES: tuple[str, ...] = (
    "TEMPORAL_CONTINUITY.P102G",
    "RESEARCH_CANARY.P103",
    "YGGDRASIL.P###",
    "ARTIFACT_CONTRACT.P###",
)

_REQUIRED_SOURCE_PATHS: tuple[str, ...] = (
    SOURCE_AUDIT_PATH,
    CONTINUITY_SPINE_PATH,
    BADGES_PATH,
    README_PATH,
    AGENTS_PATH,
    PLANS_PATH,
    REGISTRY_PATH,
)


def _read_json(root: Path, rel_path: str) -> dict[str, Any]:
    try:
        parsed = json.loads((root / rel_path).read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _file_hash(root: Path, rel_path: str) -> str:
    try:
        return hashlib.sha256((root / rel_path).read_bytes()).hexdigest()
    except OSError:
        return "NOT_COMPUTABLE"


def _source_presence(root: Path) -> list[dict[str, Any]]:
    return [
        {
            "path": rel_path,
            "observed": (root / rel_path).exists(),
            "sha256": _file_hash(root, rel_path),
        }
        for rel_path in _REQUIRED_SOURCE_PATHS
    ]


def _source_state(
    audit: dict[str, Any],
    spine: dict[str, Any],
    badges: dict[str, Any],
) -> dict[str, Any]:
    audit_state = audit.get("source_state")
    if not isinstance(audit_state, dict):
        audit_state = {}
    signals = badges.get("signals") if isinstance(badges.get("signals"), dict) else {}
    return {
        "audit_collision_count": len(audit.get("collisions", []))
        if isinstance(audit.get("collisions"), list)
        else "NOT_COMPUTABLE",
        "audit_observed_namespace_count": len(audit.get("observed_namespaces", []))
        if isinstance(audit.get("observed_namespaces"), list)
        else "NOT_COMPUTABLE",
        "audit_orphaned_reference_count": len(audit.get("orphaned_references", []))
        if isinstance(audit.get("orphaned_references"), list)
        else "NOT_COMPUTABLE",
        "canon": signals.get("canon_status", audit_state.get("canon", "NOT_COMPUTABLE")),
        "downstream": audit_state.get("downstream", audit.get("recommended_next_lane", "NOT_COMPUTABLE")),
        "governance": signals.get(
            "governance_status",
            audit_state.get("governance", "NOT_COMPUTABLE"),
        ),
        "highest_observed_lane": spine.get(
            "highest_lane",
            audit_state.get("highest_observed_lane", "NOT_COMPUTABLE"),
        ),
        "lane_count": spine.get(
            "lane_count",
            audit_state.get("lane_count", "NOT_COMPUTABLE"),
        ),
    }


def _audit_collision_numbers(audit: dict[str, Any]) -> list[str]:
    collisions = audit.get("collisions")
    if not isinstance(collisions, list):
        return []
    return sorted(
        {
            collision.get("p_number")
            for collision in collisions
            if isinstance(collision, dict) and isinstance(collision.get("p_number"), str)
        }
    )


def _critical_ambiguities(audit: dict[str, Any]) -> list[dict[str, Any]]:
    collisions = audit.get("collisions")
    if not isinstance(collisions, list):
        return []
    targets = {"P103", "P104", "P105", "P106", "P107"}
    rows: list[dict[str, Any]] = []
    for collision in collisions:
        if not isinstance(collision, dict) or collision.get("p_number") not in targets:
            continue
        namespaces = collision.get("namespaces")
        rows.append(
            {
                "ambiguity": "P103_TO_P107_RESEARCH_BRANCH_NAME_COLLISION",
                "p_number": collision["p_number"],
                "namespaces": sorted(namespaces) if isinstance(namespaces, list) else [],
                "required_resolution": "Preserve research-canary meaning; block temporal operator interpretation unless separately authorized.",
            }
        )
    return sorted(rows, key=lambda row: row["p_number"])


def _migration_phases() -> list[dict[str, Any]]:
    return [
        {
            "phase": "PHASE_0_FREEZE_AND_INVENTORY",
            "objective": "Keep P102G as the highest observed lane and use the namespace audit as the read-only evidence base.",
            "allowed_actions": ["read_source_artifacts", "compare_counts", "draft_policy"],
            "exit_gate": "source_state_matches_P102G_58_FROZEN_ADVISORY_ONLY_NOT_COMPUTABLE",
        },
        {
            "phase": "PHASE_1_DOCTRINE_ADOPTION_PLAN",
            "objective": "Adopt hybrid global IDs plus branch-local aliases in README, AGENTS, and PLANS doctrine without renaming files.",
            "allowed_actions": ["documentation_plan_only", "define_alias_rules"],
            "exit_gate": "doctrine_text_reviewed_without_runtime_or_canon_mutation",
        },
        {
            "phase": "PHASE_2_STATUS_SURFACE_TRANSITION_PLAN",
            "objective": "Plan status fields that can display canonical_global_lane_id and branch_local_alias side by side.",
            "allowed_actions": ["schema_design", "status_surface_design"],
            "exit_gate": "backwards_compatible_fields_defined",
        },
        {
            "phase": "PHASE_3_COLLISION_REMEDIATION_PLAN",
            "objective": "Prioritize P103-P107 research-canary versus temporal-continuity ambiguity before lower-risk collisions.",
            "allowed_actions": ["rank_collisions", "write_validation_plan"],
            "exit_gate": "critical_collision_resolution_order_approved_by_future_operator_decision",
        },
        {
            "phase": "PHASE_4_STABILIZATION_WINDOW",
            "objective": "Run repeated deterministic validations before any future migration execution proposal.",
            "allowed_actions": ["validation_only", "drift_check_only", "audit_review_only"],
            "exit_gate": "stabilization_window_complete_without_drift_or_authority_escalation",
        },
    ]


def _compatibility_rules() -> list[dict[str, str]]:
    return [
        {
            "rule_id": "COMPAT_001",
            "rule": "Existing numeric P-lane strings remain readable and must not be rewritten by this plan.",
        },
        {
            "rule_id": "COMPAT_002",
            "rule": "Composite aliases may be added in future surfaces only as advisory metadata until separately promoted.",
        },
        {
            "rule_id": "COMPAT_003",
            "rule": "P103-P107 keep research-canary meaning in repo history; temporal operator P103-like routes remain NOT_COMPUTABLE without explicit evidence.",
        },
        {
            "rule_id": "COMPAT_004",
            "rule": "Status surfaces must preserve highest_lane=P102G and lane_count=58 during planning-only work.",
        },
        {
            "rule_id": "COMPAT_005",
            "rule": "Artifact consumers must accept legacy lane_id while new consumers may read composite_lane_id when present.",
        },
    ]


def _naming_rules() -> dict[str, list[dict[str, str]]]:
    return {
        "artifact_naming_policy": [
            {
                "rule_id": "ARTIFACT_NAME_001",
                "rule": "Do not rename existing artifact directories during planning.",
            },
            {
                "rule_id": "ARTIFACT_NAME_002",
                "rule": "Future composite-aware artifacts should expose namespace_id and branch_local_alias fields inside payloads before path changes are considered.",
            },
        ],
        "composite_identifier_format": [
            {
                "rule_id": "COMPOSITE_ID_001",
                "rule": "Format is <NAMESPACE_ID>.<P_LANE_ID> using uppercase namespace tokens and existing P-lane spelling.",
            },
            {
                "rule_id": "COMPOSITE_ID_002",
                "rule": "Examples: TEMPORAL_CONTINUITY.P102G, RESEARCH_CANARY.P103, YGGDRASIL.P###, ARTIFACT_CONTRACT.P###.",
            },
        ],
        "doctrine_naming_policy": [
            {
                "rule_id": "DOCTRINE_001",
                "rule": "README, AGENTS, and PLANS should describe canonical global IDs separately from branch-local aliases.",
            },
            {
                "rule_id": "DOCTRINE_002",
                "rule": "Documentation must not imply that branch-local aliases grant routing or execution authority.",
            },
        ],
        "runner_naming_policy": [
            {
                "rule_id": "RUNNER_NAME_001",
                "rule": "Keep existing runner filenames stable; future namespace-aware runners may add payload metadata before any filename migration.",
            }
        ],
        "schema_naming_policy": [
            {
                "rule_id": "SCHEMA_NAME_001",
                "rule": "Keep existing schema filenames stable; future schemas may add optional composite_lane_id fields under explicit compatibility gates.",
            }
        ],
    }


def _remediation_order(audit: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    collision_numbers = _audit_collision_numbers(audit)
    critical = [p for p in ("P103", "P104", "P105", "P106", "P107") if p in collision_numbers]
    other = [p for p in collision_numbers if p not in set(critical)]
    orphaned = audit.get("orphaned_references")
    orphaned_count = len(orphaned) if isinstance(orphaned, list) else "NOT_COMPUTABLE"
    return {
        "collision_remediation_order": [
            {
                "order": 1,
                "target": critical,
                "reason": "Critical research-canary versus temporal-continuity interpretation ambiguity.",
            },
            {
                "order": 2,
                "target": other,
                "reason": "Remaining namespace collisions after critical ambiguity is stabilized.",
            },
        ],
        "orphaned_reference_remediation_order": [
            {
                "order": 1,
                "target": "recommended_next_lane references marked MISSING_REPO_EVIDENCE",
                "observed_count": orphaned_count,
                "action": "Classify each as documentation drift, missing source evidence, or intentionally blocked NOT_COMPUTABLE handoff.",
            },
            {
                "order": 2,
                "target": "non-lane terminal markers",
                "action": "Preserve terminal marker semantics unless future doctrine changes them.",
            },
        ],
    }


def _risk_register() -> list[dict[str, str]]:
    return [
        {
            "risk_id": "RISK_NAMESPACE_ALIAS_ESCALATION",
            "risk": "Composite aliases could be mistaken for routing authority.",
            "mitigation": "Keep all alias fields advisory-only and require separate governance for any routing use.",
        },
        {
            "risk_id": "RISK_STATUS_SURFACE_DRIFT",
            "risk": "Status pages could imply lane-count or highest-lane migration before evidence exists.",
            "mitigation": "Preserve P102G, lane_count 58, FROZEN, ADVISORY_ONLY, and NOT_COMPUTABLE in planning artifacts.",
        },
        {
            "risk_id": "RISK_RESEARCH_TEMPORAL_COLLISION",
            "risk": "P103-P107 could be interpreted as temporal operator authorization sequence instead of research-canary history.",
            "mitigation": "Require RESEARCH_CANARY.P103-P107 aliases and keep temporal operator P103-like route blocked.",
        },
        {
            "risk_id": "RISK_CONSUMER_BREAKAGE",
            "risk": "Downstream consumers may only understand legacy numeric lane_id fields.",
            "mitigation": "Add composite IDs only as additive metadata in future work; do not remove legacy lane_id fields.",
        },
    ]


def _validation_gates() -> list[dict[str, Any]]:
    commands = [
        "python -m pytest -q tests/test_continuity_namespace_migration_plan.py",
        "python -m ruff check core/continuity_namespace_migration_plan.py scripts/run_continuity_namespace_migration_plan.py tests/test_continuity_namespace_migration_plan.py",
        "python scripts/artifact/run_artifact_regeneration.py --check-drift",
        "python scripts/run_fast_ci.py",
        "node scripts/continuity-spine.js && node scripts/counts.js",
        "python scripts/run_p64_manifest_source_hash_gate.py",
        "python -m pip_audit",
    ]
    return [
        {
            "gate_id": f"VALIDATION_{index:03d}",
            "command": command,
            "required_before_future_execution": True,
        }
        for index, command in enumerate(commands, start=1)
    ]


def build_continuity_namespace_migration_plan(
    repo_root: Path | str | None = None,
) -> dict[str, Any]:
    root = Path(repo_root) if repo_root is not None else Path.cwd()
    audit = _read_json(root, SOURCE_AUDIT_PATH)
    spine = _read_json(root, CONTINUITY_SPINE_PATH)
    badges = _read_json(root, BADGES_PATH)
    source_state = _source_state(audit, spine, badges)
    remediation = _remediation_order(audit)

    source_policy = "NOT_COMPUTABLE"
    recommendation = audit.get("namespace_policy_recommendation")
    if isinstance(recommendation, dict):
        source_policy = recommendation.get("recommended_policy", "NOT_COMPUTABLE")

    packet: dict[str, Any] = {
        "advisory_only": True,
        "artifact_type": ARTIFACT_TYPE,
        "audit_only": True,
        "authority_locks": {name: False for name in _DENIED_AUTHORITY},
        "authorization_authority": False,
        "authorization_granted": False,
        "authorization_record_created": False,
        "authorization_record_creation_authority": False,
        "backwards_compatibility_rules": _compatibility_rules(),
        "blocked_actions": list(_BLOCKED_ACTIONS),
        "canon_promotion": False,
        "canonical_global_id_policy": {
            "policy_id": "CANONICAL_GLOBAL_ID_POLICY_001",
            "rule": "Canonical global continuity IDs remain the observed spine lane IDs until a separately authorized migration changes them.",
            "current_highest_global_id": source_state["highest_observed_lane"],
            "current_lane_count": source_state["lane_count"],
        },
        "composite_id_recommendation_examples": list(_COMPOSITE_ID_EXAMPLES),
        "denied_authority": list(_DENIED_AUTHORITY),
        "execution_authority": False,
        "explicit_non_execution_boundary": {
            "valid_for_execution": False,
            "route_authority": False,
            "mutation_authority": False,
            "reason": "Migration plan is advisory-only and cannot rename, move, rewrite, execute, authorize, or mint.",
        },
        "forecast_influence": False,
        "migration_phases": _migration_phases(),
        "naming_rules": _naming_rules(),
        "packet_source_inputs": _source_presence(root),
        "plan_id": PLAN_ID,
        "production_activation": False,
        "projection_only": True,
        "recommended_next_action": "REVIEW_HYBRID_NAMESPACE_POLICY_AND_PREPARE_ADVISORY_DOCTRINE_PATCH",
        "recommended_next_lane": "NOT_COMPUTABLE",
        "record_creation_authority": False,
        "remediation_order": remediation,
        "risk_register": _risk_register(),
        "runtime_authority": False,
        "scheduler_mutation": False,
        "selected_policy": SELECTED_POLICY,
        "source_audit_id": audit.get("audit_id", "NOT_COMPUTABLE"),
        "source_audit_policy": source_policy,
        "source_state": source_state,
        "stabilization_window": {
            "required": True,
            "minimum_validation_passes": 3,
            "drift_allowed": False,
            "authority_escalation_allowed": False,
            "completion_condition": "Three consecutive validation-only passes with unchanged P102G source state and no new downstream lane.",
        },
        "status_surface_transition_policy": {
            "policy_id": "STATUS_SURFACE_TRANSITION_POLICY_001",
            "rule": "Future status surfaces may add composite namespace metadata only additively while preserving legacy highest_lane and lane_count fields.",
            "preserve_highest_lane": "P102G",
            "preserve_lane_count": 58,
        },
        "token_minting_allowed": False,
        "token_minting_authority": False,
        "valid_for_execution": False,
        "validation_gates": _validation_gates(),
    }
    packet["critical_ambiguities"] = _critical_ambiguities(audit)
    packet["packet_hash"] = canonical_hash(packet)
    return packet


def write_continuity_namespace_migration_plan(
    path: Path | str,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
