from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "LiveProjectionHealthMigrationArtifactReceipt.v1"
STATUS = "LIVE_PROJECTION_HEALTH_MIGRATION_ARTIFACT_READY_ADVISORY_ONLY"
BRIER_SCORE = "0.10"
SLICE_ID = "LOOP-805-SLICE-66"
NOTION_BOARD_URL = "https://app.notion.com/p/3843e8ba2f5c819480d0f2c5ffce6254"
DEFAULT_OUT_PATH = "out/audit/live_projection_health_migration_artifact_001.latest.json"

SUBSYSTEM_HEALTH_RECEIPT_PATH = "out/audit/subsystem_health_dashboard_001.latest.json"
MIGRATION_RUNNER_RECEIPT_PATH = "out/audit/continuity_namespace_migration_run_001.latest.json"
ARTIFACT_CLASSIFIER_RECEIPT_PATH = "out/audit/artifact_registry_classifier_001.latest.json"
PROJECTION_BUNDLE_PATH = "apps/aal-viz-live-console/public/projection-bundle.json"
BUILD_SCRIPT_PATH = "scripts/build_aal_viz_projection_bundle.py"
LAYOUT_PATH = "apps/aal-viz-live-console/src/components/Layout.tsx"
PANEL_PATH = (
    "apps/aal-viz-live-console/src/components/CombinedHealthMigrationArtifactPanel.tsx"
)
TYPES_PATH = "apps/aal-viz-live-console/src/types.ts"
SAMPLE_BUNDLE_PATH = "apps/aal-viz-live-console/src/data/sampleProjectionBundle.ts"

SOURCE_PATHS = (
    SUBSYSTEM_HEALTH_RECEIPT_PATH,
    MIGRATION_RUNNER_RECEIPT_PATH,
    ARTIFACT_CLASSIFIER_RECEIPT_PATH,
    PROJECTION_BUNDLE_PATH,
    BUILD_SCRIPT_PATH,
    LAYOUT_PATH,
    PANEL_PATH,
    TYPES_PATH,
    SAMPLE_BUNDLE_PATH,
    "core/generated_artifact_registry.py",
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


def _normalize_findings(
    source: str,
    findings: list[dict[str, Any]] | Any,
) -> list[dict[str, str]]:
    if not isinstance(findings, list):
        return []
    rows: list[dict[str, str]] = []
    for finding in findings[:3]:
        if not isinstance(finding, dict):
            continue
        rows.append(
            {
                "source": source,
                "code": str(finding.get("code", "UNKNOWN")),
                "severity": str(finding.get("severity", "INFO")),
                "detail": str(finding.get("detail", "No detail supplied.")),
            }
        )
    return rows


def _migration_findings(
    runner_payload: dict[str, Any],
    runner_status: str,
) -> list[dict[str, str]]:
    if runner_status != "OBSERVED":
        return [
            {
                "source": "MIGRATION",
                "code": f"MIGRATION_RUNNER_{runner_status}",
                "severity": "MEDIUM",
                "detail": "Migration runner receipt is unavailable, so drilldown stays fail-closed.",
            }
        ]

    requested = runner_payload.get("requested_execution_posture", {})
    blocked_actions = runner_payload.get("blocked_actions", [])
    safe_next_surface = str(
        runner_payload.get("safe_next_surface", "NOT_COMPUTABLE")
    )
    findings: list[dict[str, str]] = [
        {
            "source": "MIGRATION",
            "code": "RUNNER_EXECUTION_POSTURE",
            "severity": "LOW",
            "detail": (
                f"Requested execution posture is {requested.get('result', 'NOT_COMPUTABLE')}: "
                f"{requested.get('reason', 'No reason supplied.')}"
            ),
        },
        {
            "source": "MIGRATION",
            "code": "RUNNER_BLOCKED_ACTIONS_PRESENT",
            "severity": "MEDIUM",
            "detail": (
                f"{len(blocked_actions) if isinstance(blocked_actions, list) else 0} migration "
                "action classes remain closed under advisory-only authority."
            ),
        },
        {
            "source": "MIGRATION",
            "code": "SAFE_NEXT_SURFACE_ROUTE",
            "severity": "LOW",
            "detail": f"Current safe next surface remains {safe_next_surface}.",
        },
    ]
    return findings


def build_combined_health_migration_artifact_posture(
    *,
    repo_root: str | Path = ".",
) -> tuple[dict[str, Any], list[str]]:
    root = Path(repo_root)
    dashboard_payload, dashboard_status = _load_json(root / SUBSYSTEM_HEALTH_RECEIPT_PATH)
    runner_payload, runner_status = _load_json(root / MIGRATION_RUNNER_RECEIPT_PATH)
    classifier_payload, classifier_status = _load_json(root / ARTIFACT_CLASSIFIER_RECEIPT_PATH)

    observed_sources: list[str] = []
    if dashboard_status == "OBSERVED":
        observed_sources.append(SUBSYSTEM_HEALTH_RECEIPT_PATH)
    if runner_status == "OBSERVED":
        observed_sources.append(MIGRATION_RUNNER_RECEIPT_PATH)
    if classifier_status == "OBSERVED":
        observed_sources.append(ARTIFACT_CLASSIFIER_RECEIPT_PATH)

    if dashboard_status != "OBSERVED":
        return (
            {
                "source_status": dashboard_status,
                "status": "NOT_COMPUTABLE",
                "health_status": dashboard_status,
                "migration_runner_status": "NOT_COMPUTABLE",
                "artifact_lifecycle_status": "NOT_COMPUTABLE",
                "requested_execution_result": "NOT_COMPUTABLE",
                "requested_execution_reason": (
                    "Subsystem health dashboard receipt is unavailable, so combined live posture stays fail-closed."
                ),
                "safe_next_surface": "NOT_COMPUTABLE",
                "recommended_next_engineering_move": (
                    "Rebuild the subsystem health dashboard receipt before relying on the combined live projection."
                ),
                "blocked_action_count": 0,
                "blocked_action_sample": [],
                "stage_count": 0,
                "stage_posture_summary": {},
                "subsystem_count": 0,
                "missing_contract_count": 0,
                "managed_artifact_count": 0,
                "orphaned_artifact_count": 0,
                "ambiguous_artifact_count": 0,
                "blocked_continuity_edge_count": 0,
                "findings_by_source": {
                    "health": [
                        {
                            "source": "HEALTH",
                            "code": f"SUBSYSTEM_HEALTH_{dashboard_status}",
                            "severity": "MEDIUM",
                            "detail": "Subsystem health dashboard receipt is unavailable.",
                        }
                    ],
                    "migration": [],
                    "artifact": [],
                },
                "authority_granted": False,
            },
            observed_sources,
        )

    dashboard_migration = dashboard_payload.get("migration_runner_posture", {})
    dashboard_artifact = dashboard_payload.get("artifact_lifecycle_posture", {})
    dashboard_ownership = dashboard_payload.get("ownership_coverage_posture", {})
    dashboard_continuity = dashboard_payload.get("continuity_health_posture", {})

    health_findings = _normalize_findings(
        "HEALTH", dashboard_payload.get("top_advisory_findings", [])
    )
    artifact_findings = _normalize_findings(
        "ARTIFACT", classifier_payload.get("top_findings", [])
    )
    migration_findings = _migration_findings(runner_payload, runner_status)

    source_status = (
        "OBSERVED"
        if runner_status == "OBSERVED" and classifier_status == "OBSERVED"
        else "NOT_COMPUTABLE"
        if runner_status == "NOT_COMPUTABLE" or classifier_status == "NOT_COMPUTABLE"
        else "MISSING"
    )
    combined_status = (
        "READY_WITH_FINDINGS"
        if health_findings or migration_findings or artifact_findings
        else "READY"
    )

    requested = runner_payload.get("requested_execution_posture", {})
    blocked_actions = runner_payload.get("blocked_actions", [])
    run_stage_rows = runner_payload.get("run_stage_rows", [])

    posture = {
        "source_status": source_status,
        "status": combined_status,
        "health_status": str(
            dashboard_payload.get("status", "SUBSYSTEM_HEALTH_DASHBOARD_READY_ADVISORY_ONLY")
        ),
        "migration_runner_status": str(
            dashboard_migration.get(
                "status",
                runner_payload.get("status", "NOT_COMPUTABLE"),
            )
        ),
        "artifact_lifecycle_status": str(
            dashboard_artifact.get(
                "current_posture",
                classifier_payload.get("classification_summary", {}).get(
                    "registry_final_status",
                    "NOT_COMPUTABLE",
                ),
            )
        ),
        "requested_execution_result": str(
            requested.get(
                "result",
                dashboard_migration.get("requested_execution_result", "NOT_COMPUTABLE"),
            )
        ),
        "requested_execution_reason": str(
            requested.get(
                "reason",
                dashboard_migration.get(
                    "requested_execution_reason",
                    "Combined live posture cannot infer execution authority.",
                ),
            )
        ),
        "safe_next_surface": str(
            runner_payload.get(
                "safe_next_surface",
                dashboard_migration.get("safe_next_surface", "NOT_COMPUTABLE"),
            )
        ),
        "recommended_next_engineering_move": str(
            runner_payload.get(
                "recommended_next_engineering_move",
                dashboard_migration.get(
                    "recommended_next_engineering_move",
                    dashboard_payload.get("recommended_next_lane", "NOT_COMPUTABLE"),
                ),
            )
        ),
        "blocked_action_count": (
            len(blocked_actions)
            if isinstance(blocked_actions, list)
            else int(dashboard_migration.get("blocked_action_count", 0))
        ),
        "blocked_action_sample": (
            [str(item) for item in blocked_actions[:4]]
            if isinstance(blocked_actions, list)
            else [str(item) for item in dashboard_migration.get("blocked_action_sample", [])[:4]]
        ),
        "stage_count": (
            len(run_stage_rows)
            if isinstance(run_stage_rows, list)
            else int(dashboard_migration.get("stage_count", 0))
        ),
        "stage_posture_summary": (
            {
                str(key): int(value)
                for key, value in dashboard_migration.get("stage_posture_summary", {}).items()
            }
            if isinstance(dashboard_migration.get("stage_posture_summary", {}), dict)
            else {}
        ),
        "subsystem_count": int(dashboard_ownership.get("subsystem_count", 0)),
        "missing_contract_count": int(dashboard_ownership.get("missing_contract_count", 0)),
        "managed_artifact_count": int(dashboard_artifact.get("managed_count", 0)),
        "orphaned_artifact_count": int(dashboard_artifact.get("orphaned_count", 0)),
        "ambiguous_artifact_count": int(dashboard_artifact.get("ambiguous_count", 0)),
        "blocked_continuity_edge_count": int(
            dashboard_continuity.get("blocked_edge_count", 0)
        ),
        "findings_by_source": {
            "health": health_findings,
            "migration": migration_findings,
            "artifact": artifact_findings,
        },
        "authority_granted": False,
    }
    return posture, observed_sources


def build_live_projection_health_migration_artifact_receipt(
    *,
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    source_table = [_source_row(root, path) for path in SOURCE_PATHS]
    bundle_payload, bundle_status = _load_json(root / PROJECTION_BUNDLE_PATH)
    posture, observed_sources = build_combined_health_migration_artifact_posture(
        repo_root=root
    )
    bundle_posture = bundle_payload.get("combined_health_migration_artifact_posture", {})
    bundle_visible = (
        bundle_status == "OBSERVED"
        and isinstance(bundle_posture, dict)
        and str(bundle_posture.get("status")) == str(posture.get("status"))
        and str(bundle_posture.get("safe_next_surface"))
        == str(posture.get("safe_next_surface"))
        and int(bundle_posture.get("blocked_action_count", -1))
        == int(posture.get("blocked_action_count", -2))
    )

    source_status = (
        "READY"
        if bundle_visible and posture["source_status"] == "OBSERVED"
        else "READY_WITH_FINDINGS"
    )

    base = {
        "artifact_type": ARTIFACT_TYPE,
        "slice_id": SLICE_ID,
        "status": STATUS,
        "brier_score": BRIER_SCORE,
        "projection_only": True,
        "advisory_only": True,
        "notion_board_url": NOTION_BOARD_URL,
        "authority_locks": AUTHORITY_LOCKS,
        "source_status": source_status,
        "source_table": source_table,
        "canonical_source_path": SUBSYSTEM_HEALTH_RECEIPT_PATH,
        "projection_bundle_path": PROJECTION_BUNDLE_PATH,
        "combined_posture_summary": {
            "bundle_source_status": bundle_status,
            "bundle_visible": bundle_visible,
            "observed_source_artifacts": observed_sources,
            "posture": posture,
            "bundle_status": (
                str(bundle_posture.get("status", "NOT_COMPUTABLE"))
                if isinstance(bundle_posture, dict)
                else "NOT_COMPUTABLE"
            ),
            "authority_granted": False,
        },
        "touched_routes": [
            PROJECTION_BUNDLE_PATH,
            LAYOUT_PATH,
            PANEL_PATH,
            TYPES_PATH,
            SAMPLE_BUNDLE_PATH,
            "README.md",
            "PLANS.md",
            "docs/START_HERE.md",
            "docs/INDEX.md",
            "docs/artifacts/ARTIFACT_INDEX.md",
        ],
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
        "validation_plan": [
            "python scripts/build_aal_viz_projection_bundle.py",
            "python scripts/run_live_projection_health_migration_artifact_receipt.py",
            "python scripts/artifact/run_artifact_regeneration.py --artifact out/audit/live_projection_health_migration_artifact_001.latest.json",
            "python -m py_compile core/live_projection_health_migration_artifact.py scripts/run_live_projection_health_migration_artifact_receipt.py tests/test_live_projection_health_migration_artifact.py",
            "python -m pytest tests/test_live_projection_health_migration_artifact.py tests/test_build_aal_viz_projection_bundle.py tests/test_generated_artifact_registry.py -q -k combined_health_migration_artifact",
            "cd apps/aal-viz-live-console; npm test -- --run; npm run typecheck",
            "git diff --check",
        ],
        "notion_closeout_text": (
            "Slice66 complete - AAL-Viz live console now projects a combined health, migration, and artifact posture surface from repo-native receipts; subsystem health, continuity namespace migration posture, and artifact lifecycle findings are visible in one advisory panel without opening execution paths; no sandbox probe, runtime activation, canon mutation, MCP exposure, external calls, or autonomous writeback authorized. Brier Score: 0.10."
        ),
        "recommended_next_lane": (
            "Priority 2 - WebSocket hardening and reconnection posture, or a deeper combined live projection route if the operator prefers more synthesis."
        ),
        "provenance": "Notion Sprint 001 Hub + Loop 805 Slice66 + Hash: canonical_hash",
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def write_live_projection_health_migration_artifact_receipt(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
