from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "SubsystemHealthDashboardReceipt.v1"
STATUS = "SUBSYSTEM_HEALTH_DASHBOARD_READY_ADVISORY_ONLY"
BRIER_SCORE = "0.10"
SLICE_ID = "LOOP-805-SLICE-72"
NOTION_BOARD_URL = "https://app.notion.com/p/3843e8ba2f5c819480d0f2c5ffce6254"
DEFAULT_OUT_PATH = "out/audit/subsystem_health_dashboard_001.latest.json"
DOC_PATH = "docs/status/SUBSYSTEM_HEALTH_DASHBOARD.md"

OWNERSHIP_DOC_PATH = "docs/status/SUBSYSTEM_OWNERSHIP_MATRIX.md"
OWNERSHIP_RECEIPT_PATH = "out/audit/subsystem_ownership_matrix_refresh_001.latest.json"
ARTIFACT_CLASSIFIER_RECEIPT_PATH = "out/audit/artifact_registry_classifier_001.latest.json"
CONTINUITY_SPINE_PATH = "docs/status/continuity-spine.json"
CONTINUITY_DOC_PATH = "docs/lineage/CONTINUITY_LINEAGE_MAP_002.md"
CONTINUITY_RECEIPT_PATH = "out/audit/continuity_lineage_map_refresh_001.latest.json"
DOCS_NAVIGATION_RECEIPT_PATH = "out/audit/docs_navigation_refresh_001.latest.json"
VIZ_RECEIPT_PATH = "out/audit/viz01_live_feed_enhancement_receipt_001.latest.json"
MIGRATION_RUNNER_RECEIPT_PATH = (
    "out/audit/continuity_namespace_migration_run_001.latest.json"
)
MIGRATION_RUNNER_DOC_PATH = "docs/status/CONTINUITY_NAMESPACE_MIGRATION_RUNNER.md"
ALIAS_IMPLEMENTATION_DESIGN_RECEIPT_PATH = (
    "out/audit/continuity_namespace_alias_implementation_design_001.latest.json"
)
ALIAS_IMPLEMENTATION_DESIGN_DOC_PATH = (
    "docs/status/CONTINUITY_NAMESPACE_ALIAS_IMPLEMENTATION_DESIGN.md"
)

SOURCE_PATHS = (
    OWNERSHIP_DOC_PATH,
    OWNERSHIP_RECEIPT_PATH,
    "core/generated_artifact_registry.py",
    ARTIFACT_CLASSIFIER_RECEIPT_PATH,
    CONTINUITY_SPINE_PATH,
    CONTINUITY_DOC_PATH,
    CONTINUITY_RECEIPT_PATH,
    DOCS_NAVIGATION_RECEIPT_PATH,
    VIZ_RECEIPT_PATH,
    MIGRATION_RUNNER_RECEIPT_PATH,
    ALIAS_IMPLEMENTATION_DESIGN_DOC_PATH,
    ALIAS_IMPLEMENTATION_DESIGN_RECEIPT_PATH,
)

ACTIVE_RECEIPT_ROUTES = (
    DOCS_NAVIGATION_RECEIPT_PATH,
    OWNERSHIP_RECEIPT_PATH,
    ARTIFACT_CLASSIFIER_RECEIPT_PATH,
    CONTINUITY_RECEIPT_PATH,
    VIZ_RECEIPT_PATH,
    MIGRATION_RUNNER_RECEIPT_PATH,
    ALIAS_IMPLEMENTATION_DESIGN_RECEIPT_PATH,
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


def _health_posture(row: dict[str, Any]) -> str:
    if row.get("contract_owner_alignment") == "DRIFT_DETECTED":
        return "BLOCKED"
    if row.get("missing_contract_paths"):
        return "PARTIAL"
    migration_statuses = {str(item) for item in row.get("migration_statuses", [])}
    if "partial" in migration_statuses:
        return "PARTIAL"
    return "ACTIVE"


def _build_subsystem_overview_rows(
    ownership_packet: dict[str, Any],
    *,
    ownership_status: str,
    viz_packet: dict[str, Any],
    viz_status: str,
) -> list[dict[str, Any]]:
    rows = ownership_packet.get("ownership_rows", [])
    if ownership_status != "OBSERVED" or not isinstance(rows, list):
        return []

    viz_ready = (
        viz_status == "OBSERVED"
        and viz_packet.get("status") == "VIZ01_LIVE_FEED_ENHANCEMENT_READY_ADVISORY_ONLY"
    )
    overview_rows: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        subsystem = str(row.get("subsystem", "UNKNOWN"))
        evidence_note = "repo-native ownership route observed"
        if subsystem == "AAL-Viz" and viz_ready:
            evidence_note = "Slice52 VIZ live-feed receipt observed"
        overview_rows.append(
            {
                "subsystem": subsystem,
                "health_posture": _health_posture(row),
                "pipeline_count": int(row.get("pipeline_count", 0)),
                "contract_alignment": row.get("contract_owner_alignment", "NOT_COMPUTABLE"),
                "migration_statuses": list(row.get("migration_statuses", [])),
                "next_action": row.get("next_action", "NOT_COMPUTABLE"),
                "evidence_note": evidence_note,
                "authority_granted": False,
            }
        )
    return overview_rows


def _ownership_coverage_posture(
    ownership_packet: dict[str, Any],
    *,
    ownership_status: str,
) -> dict[str, Any]:
    summary = ownership_packet.get("matrix_summary", {})
    if ownership_status != "OBSERVED" or not isinstance(summary, dict):
        return {
            "source_status": ownership_status,
            "subsystem_count": 0,
            "pipeline_count": 0,
            "aligned_subsystem_count": 0,
            "missing_contract_count": 0,
            "current_posture": "NOT_COMPUTABLE",
            "authority_granted": False,
        }
    missing_contract_count = int(summary.get("missing_contract_count", 0))
    return {
        "source_status": ownership_status,
        "subsystem_count": int(summary.get("subsystem_count", 0)),
        "pipeline_count": int(summary.get("pipeline_count", 0)),
        "aligned_subsystem_count": int(summary.get("aligned_subsystem_count", 0)),
        "missing_contract_count": missing_contract_count,
        "current_posture": "READY_WITH_FINDINGS" if missing_contract_count else "READY",
        "authority_granted": False,
    }


def _artifact_lifecycle_posture(
    classifier_packet: dict[str, Any],
    *,
    classifier_status: str,
) -> dict[str, Any]:
    summary = classifier_packet.get("classification_summary", {})
    family_summary = classifier_packet.get("family_summary", [])
    top_findings = classifier_packet.get("top_findings", [])
    if classifier_status != "OBSERVED" or not isinstance(summary, dict):
        return {
            "source_status": classifier_status,
            "managed_count": 0,
            "orphaned_count": 0,
            "ambiguous_count": 0,
            "no_arg_regenerable_count": 0,
            "top_family_routes": [],
            "top_findings": [],
            "current_posture": "NOT_COMPUTABLE",
            "authority_granted": False,
        }
    return {
        "source_status": classifier_status,
        "managed_count": int(summary.get("managed_count", 0)),
        "orphaned_count": int(summary.get("orphaned_count", 0)),
        "ambiguous_count": int(summary.get("ambiguous_count", 0)),
        "no_arg_regenerable_count": int(summary.get("no_arg_regenerable_count", 0)),
        "top_family_routes": family_summary[:6] if isinstance(family_summary, list) else [],
        "top_findings": top_findings[:4] if isinstance(top_findings, list) else [],
        "current_posture": summary.get("registry_final_status", "NOT_COMPUTABLE"),
        "authority_granted": False,
    }


def _continuity_health_posture(
    continuity_receipt: dict[str, Any],
    *,
    continuity_receipt_status: str,
    continuity_spine: dict[str, Any],
    continuity_spine_status: str,
) -> dict[str, Any]:
    route_groups = continuity_receipt.get("route_groups", [])
    blocked_edges = continuity_receipt.get("blocked_edges", [])
    continuity_summary = continuity_receipt.get("continuity_spine_summary", {})
    highest_lane = "NOT_COMPUTABLE"
    lane_count = 0
    if continuity_receipt_status == "OBSERVED" and isinstance(continuity_summary, dict):
        highest_lane = str(
            continuity_summary.get("highest_observed_lane", "NOT_COMPUTABLE")
        )
        lane_count = int(continuity_summary.get("lane_count", 0))
    elif continuity_spine_status == "OBSERVED":
        highest_lane = str(continuity_spine.get("highest_lane", "NOT_COMPUTABLE"))
        lane_count = int(continuity_spine.get("lane_count", 0))

    return {
        "source_status": (
            continuity_receipt_status
            if continuity_receipt_status == "OBSERVED"
            else continuity_spine_status
        ),
        "highest_observed_lane": highest_lane,
        "lane_count": lane_count,
        "route_group_count": len(route_groups) if isinstance(route_groups, list) else 0,
        "blocked_edge_count": len(blocked_edges) if isinstance(blocked_edges, list) else 0,
        "route_groups": route_groups[:4] if isinstance(route_groups, list) else [],
        "blocked_edges": blocked_edges[:5] if isinstance(blocked_edges, list) else [],
        "recommended_next_lane": continuity_receipt.get(
            "recommended_next_lane", "NOT_COMPUTABLE"
        ),
        "current_posture": (
            continuity_receipt.get("source_status", "NOT_COMPUTABLE")
            if continuity_receipt_status == "OBSERVED"
            else continuity_spine_status
        ),
        "authority_granted": False,
    }


def _viz_projection_posture(viz_packet: dict[str, Any], *, viz_status: str) -> dict[str, Any]:
    if viz_status != "OBSERVED":
        return {
            "source_status": viz_status,
            "status": "NOT_COMPUTABLE",
            "implemented_surface_count": 0,
            "connection_states": [],
            "default_poll_ms": "NOT_COMPUTABLE",
            "authority_granted": False,
        }
    public_interfaces = viz_packet.get("public_interfaces", {})
    return {
        "source_status": viz_status,
        "status": viz_packet.get("status", "NOT_COMPUTABLE"),
        "implemented_surface_count": len(viz_packet.get("implemented_surfaces", [])),
        "connection_states": list(public_interfaces.get("connection_states", [])),
        "default_poll_ms": public_interfaces.get("default_poll_ms", "NOT_COMPUTABLE"),
        "authority_granted": False,
    }


def _migration_runner_posture(
    migration_packet: dict[str, Any],
    *,
    migration_status: str,
) -> dict[str, Any]:
    if migration_status != "OBSERVED":
        return {
            "source_status": migration_status,
            "status": "NOT_COMPUTABLE",
            "migration_run_id": "NOT_COMPUTABLE",
            "requested_execution_result": "NOT_COMPUTABLE",
            "requested_execution_reason": "Migration runner receipt is not currently observable.",
            "safe_next_surface": "NOT_COMPUTABLE",
            "recommended_next_engineering_move": "NOT_COMPUTABLE",
            "blocked_action_count": 0,
            "blocked_action_sample": [],
            "stage_count": 0,
            "stage_posture_summary": {},
            "authority_granted": False,
        }
    requested_posture = migration_packet.get("requested_execution_posture", {})
    run_stage_rows = migration_packet.get("run_stage_rows", [])
    stage_posture_summary: dict[str, int] = {}
    if isinstance(run_stage_rows, list):
        for row in run_stage_rows:
            if not isinstance(row, dict):
                continue
            posture = str(row.get("resulting_advisory_posture", "NOT_COMPUTABLE"))
            stage_posture_summary[posture] = stage_posture_summary.get(posture, 0) + 1
    blocked_actions = migration_packet.get("blocked_actions", [])
    return {
        "source_status": migration_status,
        "status": migration_packet.get("status", "NOT_COMPUTABLE"),
        "migration_run_id": migration_packet.get("migration_run_id", "NOT_COMPUTABLE"),
        "requested_execution_result": requested_posture.get("result", "NOT_COMPUTABLE"),
        "requested_execution_reason": requested_posture.get(
            "reason", "NOT_COMPUTABLE"
        ),
        "safe_next_surface": migration_packet.get(
            "safe_next_surface", "NOT_COMPUTABLE"
        ),
        "recommended_next_engineering_move": migration_packet.get(
            "recommended_next_engineering_move", "NOT_COMPUTABLE"
        ),
        "blocked_action_count": len(blocked_actions)
        if isinstance(blocked_actions, list)
        else 0,
        "blocked_action_sample": blocked_actions[:4]
        if isinstance(blocked_actions, list)
        else [],
        "stage_count": len(run_stage_rows) if isinstance(run_stage_rows, list) else 0,
        "stage_posture_summary": stage_posture_summary,
        "authority_granted": False,
    }


def _alias_implementation_design_posture(
    alias_packet: dict[str, Any],
    *,
    alias_status: str,
) -> dict[str, Any]:
    if alias_status != "OBSERVED":
        return {
            "source_status": alias_status,
            "status": "NOT_COMPUTABLE",
            "implementation_state": "NOT_COMPUTABLE",
            "required_stabilization_status": "NOT_COMPUTABLE",
            "safe_next_surface": "NOT_COMPUTABLE",
            "recommended_next_engineering_move": "NOT_COMPUTABLE",
            "valid_for_implementation": False,
            "blocked_action_count": 0,
            "blocked_action_sample": [],
            "authority_granted": False,
        }

    implementation_posture = alias_packet.get("implementation_posture", {})
    blocked_action_classes = alias_packet.get("blocked_action_classes", [])
    return {
        "source_status": alias_status,
        "status": alias_packet.get("status", "NOT_COMPUTABLE"),
        "implementation_state": implementation_posture.get(
            "current_state", "NOT_COMPUTABLE"
        ),
        "required_stabilization_status": implementation_posture.get(
            "required_stabilization_status", "NOT_COMPUTABLE"
        ),
        "safe_next_surface": implementation_posture.get(
            "safe_next_surface", "NOT_COMPUTABLE"
        ),
        "recommended_next_engineering_move": alias_packet.get(
            "recommended_next_engineering_move", "NOT_COMPUTABLE"
        ),
        "valid_for_implementation": bool(
            implementation_posture.get("valid_for_implementation", False)
        ),
        "blocked_action_count": len(blocked_action_classes)
        if isinstance(blocked_action_classes, list)
        else 0,
        "blocked_action_sample": blocked_action_classes[:4]
        if isinstance(blocked_action_classes, list)
        else [],
        "authority_granted": False,
    }


def _active_receipt_routes(repo_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for relative_path in ACTIVE_RECEIPT_ROUTES:
        payload, status = _load_json(repo_root / relative_path)
        rows.append(
            {
                "artifact_path": relative_path,
                "observed": status == "OBSERVED",
                "status": payload.get("status", status) if isinstance(payload, dict) else status,
                "canonical_hash": payload.get("canonical_hash") if isinstance(payload, dict) else None,
                "authority_granted": False,
            }
        )
    return rows


def _top_advisory_findings(
    *,
    ownership_posture: dict[str, Any],
    artifact_posture: dict[str, Any],
    continuity_posture: dict[str, Any],
    viz_posture: dict[str, Any],
    migration_runner_posture: dict[str, Any],
    alias_design_posture: dict[str, Any],
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []

    if int(ownership_posture.get("missing_contract_count", 0)) > 0:
        findings.append(
            {
                "severity": "MEDIUM",
                "code": "OWNERSHIP_CONTRACT_GAPS",
                "detail": (
                    f"{ownership_posture['missing_contract_count']} subsystem contract routes remain missing, so ownership posture is only partial."
                ),
                "authority_granted": False,
            }
        )

    for row in artifact_posture.get("top_findings", []):
        if isinstance(row, dict):
            findings.append(row)

    blocked_edges = continuity_posture.get("blocked_edges", [])
    if blocked_edges:
        edge = blocked_edges[0]
        findings.append(
            {
                "severity": "MEDIUM",
                "code": "CONTINUITY_BLOCKED_EDGE",
                "detail": (
                    f"{edge.get('edge_id', 'UNKNOWN_EDGE')} remains {edge.get('current_posture', 'NOT_COMPUTABLE')} and routes to {edge.get('recommended_next_lane', 'NOT_COMPUTABLE')}."
                ),
                "authority_granted": False,
            }
        )

    if viz_posture.get("source_status") != "OBSERVED":
        findings.append(
            {
                "severity": "LOW",
                "code": "VIZ_POSTURE_UNOBSERVED",
                "detail": "Slice52 VIZ posture receipt is not currently observable from this checkout.",
                "authority_granted": False,
            }
        )

    if migration_runner_posture.get("source_status") != "OBSERVED":
        findings.append(
            {
                "severity": "LOW",
                "code": "MIGRATION_RUNNER_UNOBSERVED",
                "detail": "Slice63 continuity namespace migration runner receipt is not currently observable from this checkout.",
                "authority_granted": False,
            }
        )

    if alias_design_posture.get("source_status") != "OBSERVED":
        findings.append(
            {
                "severity": "LOW",
                "code": "ALIAS_DESIGN_ROUTE_UNOBSERVED",
                "detail": "Slice71 continuity namespace alias implementation design receipt is not currently observable from this checkout.",
                "authority_granted": False,
            }
        )
    elif not alias_design_posture.get("valid_for_implementation", False):
        findings.append(
            {
                "severity": "MEDIUM",
                "code": "ALIAS_IMPLEMENTATION_HELD",
                "detail": (
                    "Continuity namespace alias implementation remains design-only held and still requires a future stabilization receipt before any additive implementation review lane can open."
                ),
                "authority_granted": False,
            }
        )

    return findings[:6]


def _recommended_next_lane(
    *,
    ownership_posture: dict[str, Any],
    artifact_posture: dict[str, Any],
    continuity_posture: dict[str, Any],
    alias_design_posture: dict[str, Any],
) -> tuple[str, str]:
    if alias_design_posture.get("source_status") == "OBSERVED":
        return (
            "Hold continuity namespace alias lane at design-only posture",
            "Slice71 is now the current observed migration follow-on, and it explicitly keeps additive alias implementation held until a future stabilization receipt enables a later review lane.",
        )
    if (
        int(continuity_posture.get("blocked_edge_count", 0)) > 0
        or int(ownership_posture.get("missing_contract_count", 0)) > 0
    ):
        return (
            "Priority 2 - Migration Tooling follow-up",
            "Continuity blockers and missing subsystem contract routes are still visible, so a migration/readiness lane remains the highest-risk follow-on.",
        )
    if int(artifact_posture.get("managed_count", 0)) > 0:
        return (
            "Priority 2 - Live Console enhancement consuming subsystem health packet",
            "The repo-native health packet is in place and can now be projected into a richer read-only UI surface without opening authority.",
        )
    return (
        "NOT_COMPUTABLE",
        "Core dashboard inputs were not sufficiently observable to recommend a safe follow-on lane.",
    )


def build_subsystem_health_dashboard_markdown(*, repo_root: str | Path = ".") -> str:
    packet = build_subsystem_health_dashboard_receipt(repo_root=repo_root)
    lines = [
        "# Subsystem Health Dashboard",
        "",
        f"Status: `{STATUS}`",
        f"Brier Score: {BRIER_SCORE}",
        "",
        "This is a repo-native subsystem health projection that aggregates ownership routing, artifact lifecycle posture, continuity routing, continuity namespace migration runner posture, and AAL-Viz projection evidence. It is visibility only: no governance, runtime, sandbox, MCP, canon, or writeback authority is granted.",
        "",
        "## Subsystem Overview",
        "",
        "| Subsystem | Health posture | Pipelines | Contract alignment | Migration statuses | Evidence note |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in packet.get("subsystem_overview_rows", []):
        lines.append(
            "| "
            + " | ".join(
                (
                    str(row.get("subsystem", "UNKNOWN")),
                    str(row.get("health_posture", "NOT_COMPUTABLE")),
                    str(row.get("pipeline_count", 0)),
                    str(row.get("contract_alignment", "NOT_COMPUTABLE")),
                    ", ".join(str(item) for item in row.get("migration_statuses", [])),
                    str(row.get("evidence_note", "NOT_COMPUTABLE")),
                )
            )
            + " |"
        )
    ownership = packet.get("ownership_coverage_posture", {})
    artifact = packet.get("artifact_lifecycle_posture", {})
    continuity = packet.get("continuity_health_posture", {})
    viz = packet.get("viz_projection_posture", {})
    migration_runner = packet.get("migration_runner_posture", {})
    alias_design = packet.get("alias_implementation_design_posture", {})
    lines.extend(
        [
            "",
            "## Ownership Coverage Posture",
            "",
            f"- Ownership receipt: `{OWNERSHIP_RECEIPT_PATH}`",
            f"- Subsystems observed: `{ownership.get('subsystem_count', 0)}`",
            f"- Pipelines observed: `{ownership.get('pipeline_count', 0)}`",
            f"- Contract-aligned subsystems: `{ownership.get('aligned_subsystem_count', 0)}`",
            f"- Missing contract routes: `{ownership.get('missing_contract_count', 0)}`",
            "",
            "## Artifact Lifecycle / Regeneration Posture",
            "",
            f"- Managed artifacts: `{artifact.get('managed_count', 0)}`",
            f"- Orphaned artifacts: `{artifact.get('orphaned_count', 0)}`",
            f"- No-arg regenerable artifacts: `{artifact.get('no_arg_regenerable_count', 0)}`",
            "",
            "| Family | Route class | Artifact count | Managed | No-arg regenerable |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in artifact.get("top_family_routes", []):
        lines.append(
            "| "
            + " | ".join(
                (
                    str(row.get("family", "UNKNOWN")),
                    str(row.get("route_class", "NOT_COMPUTABLE")),
                    str(row.get("artifact_count", 0)),
                    str(row.get("managed_count", 0)),
                    str(row.get("no_arg_regenerable_count", 0)),
                )
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Continuity Health / Blocked-Chain Posture",
            "",
            f"- Highest observed continuity lane: `{continuity.get('highest_observed_lane', 'NOT_COMPUTABLE')}`",
            f"- Continuity lane count: `{continuity.get('lane_count', 0)}`",
            f"- Blocked continuity edges: `{continuity.get('blocked_edge_count', 0)}`",
            "",
            "| Route group | Current posture | Recommended next lane | Why this matters |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in continuity.get("route_groups", []):
        lines.append(
            "| "
            + " | ".join(
                (
                    str(row.get("label", "UNKNOWN")),
                    str(row.get("current_posture", "NOT_COMPUTABLE")),
                    str(row.get("recommended_next_lane", "NOT_COMPUTABLE")),
                    str(row.get("why_this_matters", "NOT_COMPUTABLE")),
                )
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## VIZ Projection Posture",
            "",
            f"- Slice52 posture: `{viz.get('status', 'NOT_COMPUTABLE')}`",
            f"- Implemented surfaces observed: `{viz.get('implemented_surface_count', 0)}`",
            f"- Connection states: `{', '.join(str(item) for item in viz.get('connection_states', []))}`",
            "",
            "## Continuity Namespace Migration Runner Posture",
            "",
            f"- Slice63 posture: `{migration_runner.get('status', 'NOT_COMPUTABLE')}`",
            f"- Requested execution posture: `{migration_runner.get('requested_execution_result', 'NOT_COMPUTABLE')}`",
            f"- Safe next surface: `{migration_runner.get('safe_next_surface', 'NOT_COMPUTABLE')}`",
            f"- Blocked action classes: `{migration_runner.get('blocked_action_count', 0)}`",
            "",
            "| Signal | Value |",
            "| --- | --- |",
            f"| Migration run id | `{migration_runner.get('migration_run_id', 'NOT_COMPUTABLE')}` |",
            f"| Requested execution reason | {migration_runner.get('requested_execution_reason', 'NOT_COMPUTABLE')} |",
            f"| Recommended next engineering move | {migration_runner.get('recommended_next_engineering_move', 'NOT_COMPUTABLE')} |",
            f"| Blocked action sample | {', '.join(str(item) for item in migration_runner.get('blocked_action_sample', []))} |",
            f"| Stage posture summary | {', '.join(f'{key}:{value}' for key, value in migration_runner.get('stage_posture_summary', {}).items())} |",
            "",
            "## Continuity Namespace Alias Implementation Design Posture",
            "",
            f"- Slice71 posture: `{alias_design.get('status', 'NOT_COMPUTABLE')}`",
            f"- Implementation state: `{alias_design.get('implementation_state', 'NOT_COMPUTABLE')}`",
            f"- Safe next surface: `{alias_design.get('safe_next_surface', 'NOT_COMPUTABLE')}`",
            f"- Valid for implementation: `{str(alias_design.get('valid_for_implementation', False)).lower()}`",
            "",
            "| Signal | Value |",
            "| --- | --- |",
            f"| Required stabilization status | `{alias_design.get('required_stabilization_status', 'NOT_COMPUTABLE')}` |",
            f"| Recommended next engineering move | {alias_design.get('recommended_next_engineering_move', 'NOT_COMPUTABLE')} |",
            f"| Blocked action sample | {', '.join(str(item) for item in alias_design.get('blocked_action_sample', []))} |",
            "",
            "## Top Advisory Findings",
            "",
        ]
    )
    for finding in packet.get("top_advisory_findings", []):
        lines.append(
            f"- `{finding.get('code', 'UNKNOWN')}` ({finding.get('severity', 'LOW')}): {finding.get('detail', 'NOT_COMPUTABLE')}"
        )
    lines.extend(
        [
            "",
            "## Why This Matters",
            "",
            "Priority 3 created the routing, ownership, artifact, and continuity inputs needed for a repo-native health surface. Slice61 compresses those inputs into one deterministic dashboard so contributors can evaluate subsystem posture without conflating visibility with authority. Slice64 extends that surface so the continuity namespace migration run-layer is visible in the same advisory dashboard instead of living as a disconnected migration-only receipt. Slice72 keeps that route current by surfacing the merged alias implementation design posture instead of pointing to it as future work.",
            "",
            "## Next Action",
            "",
            "- Receipt: [`../../out/audit/subsystem_health_dashboard_001.latest.json`](../../out/audit/subsystem_health_dashboard_001.latest.json)",
            "- Runner: [`../../scripts/run_subsystem_health_dashboard_receipt.py`](../../scripts/run_subsystem_health_dashboard_receipt.py)",
            "- Migration runbook: [`CONTINUITY_NAMESPACE_MIGRATION_RUNNER.md`](CONTINUITY_NAMESPACE_MIGRATION_RUNNER.md)",
            "- Alias implementation design route: [`CONTINUITY_NAMESPACE_ALIAS_IMPLEMENTATION_DESIGN.md`](CONTINUITY_NAMESPACE_ALIAS_IMPLEMENTATION_DESIGN.md)",
            f"- Recommended next lane: `{packet.get('recommended_next_lane', 'NOT_COMPUTABLE')}`",
            "- Keep `ORACLE_SANDBOX_PROBE_GATE_CONFIRMED` unissued unless the operator explicitly provides it in a future gate.",
            "",
            "## Boundary Note",
            "",
            "Projection and status routing only. No sandbox probe, runtime activation, canon mutation, MCP exposure, external calls, or autonomous Notion/GitHub writeback is authorized.",
            "",
            "Provenance: Notion Sprint 001 Hub + Loop 805 Slice72 + Hash: receipt canonical_hash",
            "",
        ]
    )
    return "\n".join(lines)


def build_subsystem_health_dashboard_receipt(
    *, repo_root: str | Path = "."
) -> dict[str, Any]:
    root = Path(repo_root)
    source_table = [_source_row(root, path) for path in SOURCE_PATHS]

    ownership_packet, ownership_status = _load_json(root / OWNERSHIP_RECEIPT_PATH)
    classifier_packet, classifier_status = _load_json(root / ARTIFACT_CLASSIFIER_RECEIPT_PATH)
    continuity_receipt, continuity_receipt_status = _load_json(
        root / CONTINUITY_RECEIPT_PATH
    )
    continuity_spine, continuity_spine_status = _load_json(root / CONTINUITY_SPINE_PATH)
    viz_packet, viz_status = _load_json(root / VIZ_RECEIPT_PATH)
    migration_runner_packet, migration_runner_status = _load_json(
        root / MIGRATION_RUNNER_RECEIPT_PATH
    )
    alias_design_packet, alias_design_status = _load_json(
        root / ALIAS_IMPLEMENTATION_DESIGN_RECEIPT_PATH
    )

    subsystem_overview_rows = _build_subsystem_overview_rows(
        ownership_packet,
        ownership_status=ownership_status,
        viz_packet=viz_packet,
        viz_status=viz_status,
    )
    ownership_coverage_posture = _ownership_coverage_posture(
        ownership_packet,
        ownership_status=ownership_status,
    )
    artifact_lifecycle_posture = _artifact_lifecycle_posture(
        classifier_packet,
        classifier_status=classifier_status,
    )
    continuity_health_posture = _continuity_health_posture(
        continuity_receipt,
        continuity_receipt_status=continuity_receipt_status,
        continuity_spine=continuity_spine,
        continuity_spine_status=continuity_spine_status,
    )
    viz_projection_posture = _viz_projection_posture(viz_packet, viz_status=viz_status)
    migration_runner_posture = _migration_runner_posture(
        migration_runner_packet,
        migration_status=migration_runner_status,
    )
    alias_implementation_design_posture = _alias_implementation_design_posture(
        alias_design_packet,
        alias_status=alias_design_status,
    )
    active_receipt_routes = _active_receipt_routes(root)
    top_advisory_findings = _top_advisory_findings(
        ownership_posture=ownership_coverage_posture,
        artifact_posture=artifact_lifecycle_posture,
        continuity_posture=continuity_health_posture,
        viz_posture=viz_projection_posture,
        migration_runner_posture=migration_runner_posture,
        alias_design_posture=alias_implementation_design_posture,
    )
    recommended_next_lane, recommended_next_lane_reason = _recommended_next_lane(
        ownership_posture=ownership_coverage_posture,
        artifact_posture=artifact_lifecycle_posture,
        continuity_posture=continuity_health_posture,
        alias_design_posture=alias_implementation_design_posture,
    )

    observed_sources = sum(
        1 for row in source_table if row.get("source_status") == "OBSERVED"
    )
    source_status = (
        "NOT_COMPUTABLE"
        if observed_sources == 0
        else "READY_WITH_FINDINGS"
        if top_advisory_findings
        else "READY"
    )

    packet: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "slice_id": SLICE_ID,
        "status": STATUS,
        "brier_score": BRIER_SCORE,
        "advisory_only": True,
        "projection_only": True,
        "notion_board_url": NOTION_BOARD_URL,
        "claimed_card": "Priority 2 - Subsystem Health Dashboard alias design alignment refresh",
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
        "subsystem_overview_rows": subsystem_overview_rows,
        "ownership_coverage_posture": ownership_coverage_posture,
        "artifact_lifecycle_posture": artifact_lifecycle_posture,
        "continuity_health_posture": continuity_health_posture,
        "viz_projection_posture": viz_projection_posture,
        "migration_runner_posture": migration_runner_posture,
        "alias_implementation_design_posture": alias_implementation_design_posture,
        "active_receipt_routes": active_receipt_routes,
        "top_advisory_findings": top_advisory_findings,
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommended_next_lane_reason,
        "doc_path": DOC_PATH,
        "touched_docs": [
            "README.md",
            "PLANS.md",
            "docs/START_HERE.md",
            "docs/INDEX.md",
            "docs/artifacts/ARTIFACT_INDEX.md",
            DOC_PATH,
        ],
        "notion_closeout_text": (
            "Slice72 complete - Subsystem health dashboard now surfaces the merged continuity namespace alias implementation design posture alongside ownership, artifact lifecycle, continuity, migration-runner, and VIZ routes; the dashboard no longer points at Slice71 as future work and instead reflects the current held design-only state; no sandbox probe, runtime activation, canon mutation, MCP exposure, external calls, or autonomous writeback authorized. Brier Score: 0.10."
        ),
        "validation_plan": [
            "python scripts/run_subsystem_health_dashboard_receipt.py",
            "python scripts/run_artifact_regeneration.py --artifact out/audit/subsystem_health_dashboard_001.latest.json",
            "python -m py_compile core/subsystem_health_dashboard.py scripts/run_subsystem_health_dashboard_receipt.py tests/test_subsystem_health_dashboard.py",
            "python -m pytest tests/test_subsystem_health_dashboard.py tests/test_generated_artifact_registry.py -q -k \"subsystem_health_dashboard or continuity_namespace_migration_run or continuity_namespace_alias_implementation_design\"",
            "git diff --check",
        ],
        "provenance": "Notion Sprint 001 Hub + Loop 805 Slice72 + Hash: canonical_hash",
    }
    packet["canonical_hash"] = canonical_hash(packet)
    return packet


def write_subsystem_health_dashboard_receipt(
    path: str | Path, packet: dict[str, Any]
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    write_canonical_json(target, packet)
