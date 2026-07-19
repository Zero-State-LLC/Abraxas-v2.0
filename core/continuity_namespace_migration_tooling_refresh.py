from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ContinuityNamespaceMigrationToolingRefreshReceipt.v1"
STATUS = "CONTINUITY_NAMESPACE_MIGRATION_TOOLING_REFRESH_READY_ADVISORY_ONLY"
BRIER_SCORE = "0.10"
SLICE_ID = "LOOP-805-SLICE-62"
NOTION_BOARD_URL = "https://app.notion.com/p/3843e8ba2f5c819480d0f2c5ffce6254"
DEFAULT_OUT_PATH = "out/audit/continuity_namespace_migration_tooling_refresh_001.latest.json"
STATUS_DOC_PATH = "docs/status/CONTINUITY_NAMESPACE_MIGRATION_STATUS.md"

CONTINUITY_NAMESPACE_AUDIT_PATH = "out/continuity_namespace_audit/latest.json"
CONTINUITY_NAMESPACE_MIGRATION_PLAN_PATH = "out/continuity_namespace_migration_plan/latest.json"
CONTINUITY_NAMESPACE_STABILIZATION_RECEIPT_PATH = (
    "out/continuity_namespace_stabilization_receipt/latest.json"
)
CONTINUITY_NAMESPACE_READINESS_REVIEW_PATH = (
    "out/continuity_namespace_readiness_review/latest.json"
)
CONTINUITY_NAMESPACE_ALIAS_PLAN_PATH = "out/continuity_namespace_alias_plan/latest.json"
CONTINUITY_SPINE_PATH = "docs/status/continuity-spine.json"
CONTINUITY_LINEAGE_MAP_PATH = "docs/lineage/CONTINUITY_LINEAGE_MAP_002.md"
SUBSYSTEM_HEALTH_DASHBOARD_RECEIPT_PATH = (
    "out/audit/subsystem_health_dashboard_001.latest.json"
)

SOURCE_PATHS = (
    CONTINUITY_NAMESPACE_AUDIT_PATH,
    CONTINUITY_NAMESPACE_MIGRATION_PLAN_PATH,
    CONTINUITY_NAMESPACE_STABILIZATION_RECEIPT_PATH,
    CONTINUITY_NAMESPACE_READINESS_REVIEW_PATH,
    CONTINUITY_NAMESPACE_ALIAS_PLAN_PATH,
    CONTINUITY_SPINE_PATH,
    CONTINUITY_LINEAGE_MAP_PATH,
    "core/generated_artifact_registry.py",
    SUBSYSTEM_HEALTH_DASHBOARD_RECEIPT_PATH,
)

STACK_SOURCE_LABELS = (
    (
        "audit",
        CONTINUITY_NAMESPACE_AUDIT_PATH,
        "ACTIVE MIGRATION ROUTE",
        "Namespace audit present as the read-only evidence base.",
    ),
    (
        "migration_plan",
        CONTINUITY_NAMESPACE_MIGRATION_PLAN_PATH,
        "ACTIVE MIGRATION ROUTE",
        "Hybrid namespace migration plan present with additive-only policy.",
    ),
    (
        "stabilization_receipt",
        CONTINUITY_NAMESPACE_STABILIZATION_RECEIPT_PATH,
        "ACTIVE MIGRATION ROUTE",
        "Stabilization receipt present and holding implementation authority closed.",
    ),
    (
        "readiness_review",
        CONTINUITY_NAMESPACE_READINESS_REVIEW_PATH,
        "ACTIVE MIGRATION ROUTE",
        "Readiness review present and routing safely to the additive alias plan.",
    ),
    (
        "alias_plan",
        CONTINUITY_NAMESPACE_ALIAS_PLAN_PATH,
        "ACTIVE MIGRATION ROUTE",
        "Additive alias plan present as the current safe next continuity namespace surface.",
    ),
    (
        "continuity_spine",
        CONTINUITY_SPINE_PATH,
        "HISTORICAL REFERENCE",
        "Continuity spine preserves the observed lane inventory and highest lane.",
    ),
    (
        "lineage_map",
        CONTINUITY_LINEAGE_MAP_PATH,
        "HISTORICAL REFERENCE",
        "Continuity lineage map provides current contributor-facing routing over the temporal spine.",
    ),
    (
        "subsystem_health_dashboard",
        SUBSYSTEM_HEALTH_DASHBOARD_RECEIPT_PATH,
        "HISTORICAL REFERENCE",
        "Subsystem health dashboard provides the Priority 2 routing entry into migration tooling.",
    ),
)

AUTHORITY_LOCKS = {
    "canon_mutation": False,
    "external_calls": False,
    "github_writeback": False,
    "mcp_exposure": False,
    "notion_writeback": False,
    "production_activation": False,
    "runtime_activation": False,
    "runtime_mutation": False,
    "sandbox_probe_execution": False,
}


def _read_text(path: Path) -> tuple[str, str]:
    try:
        return path.read_text(encoding="utf-8"), "OBSERVED"
    except FileNotFoundError:
        return "", "MISSING"
    except OSError:
        return "", "NOT_COMPUTABLE"


def _load_json(path: Path) -> tuple[dict[str, Any], str]:
    text, status = _read_text(path)
    if status != "OBSERVED":
        return {}, status
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return {}, "NOT_COMPUTABLE"
    if not isinstance(payload, dict):
        return {}, "NOT_COMPUTABLE"
    return payload, "OBSERVED"


def _source_row(repo_root: Path, relative_path: str) -> dict[str, Any]:
    path = repo_root / relative_path
    text, status = _read_text(path)
    row: dict[str, Any] = {
        "path": relative_path,
        "source_status": status,
        "line_count": len(text.splitlines()) if status == "OBSERVED" else 0,
        "authority_granted": False,
    }
    if relative_path.endswith(".json"):
        payload, json_status = _load_json(path)
        row["source_status"] = json_status
        row["top_level_key_count"] = len(payload) if json_status == "OBSERVED" else 0
    return row


def _stack_route_rows(
    repo_root: Path,
    payloads: dict[str, dict[str, Any]],
    statuses: dict[str, str],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for label, relative_path, route_class, why_this_matters in STACK_SOURCE_LABELS:
        payload = payloads.get(label, {})
        source_status = statuses.get(label, "NOT_COMPUTABLE")
        rows.append(
            {
                "source_label": label,
                "path": relative_path,
                "route_class": (
                    "NOT_COMPUTABLE / HELD"
                    if source_status != "OBSERVED"
                    else route_class
                ),
                "source_status": source_status,
                "status": payload.get("status", source_status),
                "why_this_matters": why_this_matters,
                "authority_granted": False,
            }
        )
    return rows


def _phase_rows(payloads: dict[str, dict[str, Any]], statuses: dict[str, str]) -> list[dict[str, Any]]:
    readiness = payloads.get("readiness_review", {})
    alias_plan = payloads.get("alias_plan", {})
    return [
        {
            "phase": "audit present",
            "path": CONTINUITY_NAMESPACE_AUDIT_PATH,
            "observed": statuses.get("audit") == "OBSERVED",
            "current_posture": payloads.get("audit", {}).get("source_state", {}).get(
                "governance",
                statuses.get("audit", "NOT_COMPUTABLE"),
            ),
            "next_action": "Use as the read-only migration evidence base.",
            "authority_granted": False,
        },
        {
            "phase": "migration plan present",
            "path": CONTINUITY_NAMESPACE_MIGRATION_PLAN_PATH,
            "observed": statuses.get("migration_plan") == "OBSERVED",
            "current_posture": payloads.get("migration_plan", {}).get(
                "selected_policy",
                statuses.get("migration_plan", "NOT_COMPUTABLE"),
            ),
            "next_action": "Preserve additive-only policy and route through the plan rather than renaming surfaces.",
            "authority_granted": False,
        },
        {
            "phase": "stabilization receipt present",
            "path": CONTINUITY_NAMESPACE_STABILIZATION_RECEIPT_PATH,
            "observed": statuses.get("stabilization_receipt") == "OBSERVED",
            "current_posture": payloads.get("stabilization_receipt", {}).get(
                "recommended_next_action",
                statuses.get("stabilization_receipt", "NOT_COMPUTABLE"),
            ),
            "next_action": "Keep implementation authority held until a future design slice is explicitly scoped.",
            "authority_granted": False,
        },
        {
            "phase": "readiness review present",
            "path": CONTINUITY_NAMESPACE_READINESS_REVIEW_PATH,
            "observed": statuses.get("readiness_review") == "OBSERVED",
            "current_posture": readiness.get(
                "readiness_status",
                statuses.get("readiness_review", "NOT_COMPUTABLE"),
            ),
            "next_action": readiness.get(
                "recommended_next_action",
                "DRAFT_ADVISORY_ONLY_ADDITIVE_ALIAS_PLAN",
            ),
            "authority_granted": False,
        },
        {
            "phase": "additive alias plan present",
            "path": CONTINUITY_NAMESPACE_ALIAS_PLAN_PATH,
            "observed": statuses.get("alias_plan") == "OBSERVED",
            "current_posture": alias_plan.get(
                "plan_status",
                statuses.get("alias_plan", "NOT_COMPUTABLE"),
            ),
            "next_action": alias_plan.get(
                "recommended_next_action",
                "HOLD_FOR_STABILIZATION_RECEIPT_BEFORE_IMPLEMENTATION",
            ),
            "authority_granted": False,
        },
    ]


def _critical_findings(payloads: dict[str, dict[str, Any]], statuses: dict[str, str]) -> list[dict[str, Any]]:
    readiness = payloads.get("readiness_review", {})
    findings: list[dict[str, Any]] = []

    collision_summary = readiness.get("unresolved_collision_summary", {})
    if statuses.get("readiness_review") == "OBSERVED" and isinstance(collision_summary, dict):
        findings.append(
            {
                "severity": "MEDIUM",
                "code": "P103_P107_COLLISION_CONTAINMENT",
                "detail": (
                    f"{collision_summary.get('critical_ambiguity', 'P103_TO_P107_RESEARCH_BRANCH_NAME_COLLISION')} remains "
                    f"{collision_summary.get('resolution_posture', 'NOT_COMPUTABLE')} "
                    f"across {collision_summary.get('total_collision_count', 0)} total collisions."
                ),
                "authority_granted": False,
            }
        )

    orphan_summary = readiness.get("unresolved_orphan_summary", {})
    if statuses.get("readiness_review") == "OBSERVED" and isinstance(orphan_summary, dict):
        findings.append(
            {
                "severity": "MEDIUM",
                "code": "ORPHANED_RECOMMENDED_NEXT_LANE_REFERENCES",
                "detail": (
                    f"{orphan_summary.get('total_orphaned_recommended_next_lane_references', 0)} orphaned "
                    "recommended_next_lane references remain review inputs for a future alias plan."
                ),
                "authority_granted": False,
            }
        )

    if statuses.get("alias_plan") == "OBSERVED":
        findings.append(
            {
                "severity": "MEDIUM",
                "code": "NO_ALIAS_IMPLEMENTATION_AUTHORITY",
                "detail": (
                    "The additive alias plan is emitted, but path renames, legacy ID rewrites, and alias materialization remain forbidden without a later explicit design/implementation lane."
                ),
                "authority_granted": False,
            }
        )

    for label in ("audit", "migration_plan", "stabilization_receipt", "readiness_review", "alias_plan"):
        if statuses.get(label) != "OBSERVED":
            findings.append(
                {
                    "severity": "HIGH",
                    "code": f"{label.upper()}_SOURCE_{statuses.get(label, 'NOT_COMPUTABLE')}",
                    "detail": (
                        f"{label.replace('_', ' ')} source is {statuses.get(label, 'NOT_COMPUTABLE')}, so the continuity namespace package is degraded and must stay fail-closed."
                    ),
                    "authority_granted": False,
                }
            )

    return findings[:6]


def _current_posture(payloads: dict[str, dict[str, Any]], statuses: dict[str, str]) -> tuple[str, str]:
    required = ("audit", "migration_plan", "stabilization_receipt", "readiness_review", "alias_plan")
    if any(statuses.get(name) != "OBSERVED" for name in required):
        return (
            "NOT_COMPUTABLE / HELD",
            "One or more required continuity namespace inputs are missing or unreadable, so the package remains degraded and advisory only.",
        )

    readiness = payloads["readiness_review"]
    alias_plan = payloads["alias_plan"]
    if (
        readiness.get("readiness_status") == "READY_FOR_ADDITIVE_ALIAS_PLAN"
        and alias_plan.get("plan_status") == "ADDITIVE_ALIAS_PLAN_EMITTED"
    ):
        return (
            "ACTIVE MIGRATION ROUTE",
            "The continuity namespace stack is fully present and deterministic, with the additive alias plan as the current safe next surface.",
        )

    return (
        "NOT_COMPUTABLE / HELD",
        "Continuity namespace sources are observed, but the stack posture is not in the expected additive-alias-ready state.",
    )


def build_continuity_namespace_migration_tooling_refresh_receipt(
    *,
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    source_table = [_source_row(root, path) for path in SOURCE_PATHS]

    payloads: dict[str, dict[str, Any]] = {}
    statuses: dict[str, str] = {}
    for label, relative_path in (
        ("audit", CONTINUITY_NAMESPACE_AUDIT_PATH),
        ("migration_plan", CONTINUITY_NAMESPACE_MIGRATION_PLAN_PATH),
        ("stabilization_receipt", CONTINUITY_NAMESPACE_STABILIZATION_RECEIPT_PATH),
        ("readiness_review", CONTINUITY_NAMESPACE_READINESS_REVIEW_PATH),
        ("alias_plan", CONTINUITY_NAMESPACE_ALIAS_PLAN_PATH),
        ("continuity_spine", CONTINUITY_SPINE_PATH),
        ("subsystem_health_dashboard", SUBSYSTEM_HEALTH_DASHBOARD_RECEIPT_PATH),
    ):
        payloads[label], statuses[label] = _load_json(root / relative_path)

    _, lineage_status = _read_text(root / CONTINUITY_LINEAGE_MAP_PATH)
    statuses["lineage_map"] = lineage_status
    payloads["lineage_map"] = {}

    route_class, posture_detail = _current_posture(payloads, statuses)
    findings = _critical_findings(payloads, statuses)
    source_status = (
        "NOT_COMPUTABLE"
        if not any(row.get("source_status") == "OBSERVED" for row in source_table)
        else "READY_WITH_FINDINGS"
        if findings
        else "READY"
    )

    readiness = payloads.get("readiness_review", {})
    alias_plan = payloads.get("alias_plan", {})
    continuity_spine = payloads.get("continuity_spine", {})
    dashboard = payloads.get("subsystem_health_dashboard", {})

    packet: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "slice_id": SLICE_ID,
        "status": STATUS,
        "brier_score": BRIER_SCORE,
        "advisory_only": True,
        "projection_only": True,
        "notion_board_url": NOTION_BOARD_URL,
        "claimed_card": "Priority 2 - Continuity Namespace Migration Tooling Refresh",
        "authority_locks": AUTHORITY_LOCKS,
        "boundary": {
            "sandbox_gate_issue": "#892",
            "sandbox_gate_phrase": "ORACLE_SANDBOX_PROBE_GATE_CONFIRMED",
            "sandbox_gate_issued": False,
            "canon_mutation": False,
            "external_calls": False,
            "github_writeback": False,
            "mcp_exposure": False,
            "notion_writeback": False,
            "runtime_activation": False,
        },
        "source_status": source_status,
        "source_table": source_table,
        "current_route_class": route_class,
        "current_route_detail": posture_detail,
        "stack_route_rows": _stack_route_rows(root, payloads, statuses),
        "current_repo_migration_phase_rows": _phase_rows(payloads, statuses),
        "continuity_invariants": {
            "highest_observed_lane": readiness.get(
                "source_state",
                {},
            ).get("highest_observed_lane", continuity_spine.get("highest_lane", "NOT_COMPUTABLE")),
            "lane_count": readiness.get("source_state", {}).get(
                "lane_count", continuity_spine.get("lane_count", 0)
            ),
            "governance": readiness.get("source_state", {}).get("governance", "NOT_COMPUTABLE"),
            "canon": readiness.get("source_state", {}).get("canon", "NOT_COMPUTABLE"),
            "downstream": readiness.get("source_state", {}).get("downstream", "NOT_COMPUTABLE"),
            "authority_granted": False,
        },
        "safe_next_surface": readiness.get(
            "safe_next_surface_recommendation",
            "NOT_COMPUTABLE",
        ),
        "readiness_status": readiness.get("readiness_status", "NOT_COMPUTABLE"),
        "alias_plan_status": alias_plan.get("plan_status", "NOT_COMPUTABLE"),
        "selected_policy": alias_plan.get(
            "selected_policy",
            payloads.get("migration_plan", {}).get("selected_policy", "NOT_COMPUTABLE"),
        ),
        "critical_unresolved_findings": findings,
        "current_dashboard_route": {
            "dashboard_status": dashboard.get("status", statuses.get("subsystem_health_dashboard", "NOT_COMPUTABLE")),
            "dashboard_recommended_next_lane": dashboard.get(
                "recommended_next_lane",
                "NOT_COMPUTABLE",
            ),
            "authority_granted": False,
        },
        "recommended_next_engineering_move": (
            "Additive alias implementation design slice"
            if readiness.get("readiness_status") == "READY_FOR_ADDITIVE_ALIAS_PLAN"
            else "Artifact-lineage repair follow-up if continuity packaging gaps remain"
        ),
        "recommended_next_engineering_reason": (
            "The full continuity namespace stack is present and routes safely to the additive alias plan, but implementation authority remains explicitly held."
            if readiness.get("readiness_status") == "READY_FOR_ADDITIVE_ALIAS_PLAN"
            else "The continuity namespace package is degraded or incomplete, so artifact-lineage repair is the safer follow-up."
        ),
        "doc_path": STATUS_DOC_PATH,
        "touched_docs": [
            "README.md",
            "PLANS.md",
            "docs/START_HERE.md",
            "docs/INDEX.md",
            "docs/artifacts/ARTIFACT_INDEX.md",
            STATUS_DOC_PATH,
        ],
        "validation_plan": [
            "python scripts/temporal/run_continuity_namespace_migration_tooling_refresh_receipt.py",
            "python scripts/artifact/run_artifact_regeneration.py --artifact out/audit/continuity_namespace_migration_tooling_refresh_001.latest.json",
            "python -m py_compile core/continuity_namespace_migration_tooling_refresh.py scripts/temporal/run_continuity_namespace_migration_tooling_refresh_receipt.py tests/test_continuity_namespace_migration_tooling_refresh.py",
            "python -m pytest tests/test_continuity_namespace_migration_tooling_refresh.py tests/test_generated_artifact_registry.py -q -k continuity_namespace_migration_tooling_refresh",
            "git diff --check",
        ],
        "notion_closeout_text": (
            "Slice62 complete - Continuity Namespace Migration Tooling Refresh shipped; existing continuity namespace audit, migration plan, stabilization receipt, readiness review, and additive alias plan now route through one advisory packaging receipt and status surface; no sandbox probe, runtime activation, canon mutation, MCP exposure, external calls, or autonomous writeback authorized. Brier Score: 0.10."
        ),
        "provenance": (
            "Notion Sprint 001 Hub + Loop 805 Slice62 + "
            "Hash: canonical_hash"
        ),
    }
    packet["canonical_hash"] = canonical_hash(packet)
    return packet


def write_continuity_namespace_migration_tooling_refresh_receipt(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
