from __future__ import annotations

from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "Priority2LiveConsoleMigrationCloseoutReceipt.v1"
STATUS = "PRIORITY2_LIVE_CONSOLE_MIGRATION_CLOSEOUT_READY_ADVISORY_ONLY"
BRIER_SCORE = "0.10"
SLICE_ID = "LOOP-805-SLICE-69"
NOTION_BOARD_URL = "https://app.notion.com/p/3843e8ba2f5c819480d0f2c5ffce6254"
DEFAULT_OUT_PATH = "out/audit/priority2_live_console_migration_closeout_001.latest.json"

SOURCE_PATHS = (
    "STATUS.md",
    "README.md",
    "PLANS.md",
    "docs/START_HERE.md",
    "docs/INDEX.md",
    "docs/status/SUBSYSTEM_HEALTH_DASHBOARD.md",
    "docs/status/CONTINUITY_NAMESPACE_MIGRATION_STATUS.md",
    "docs/status/CONTINUITY_NAMESPACE_MIGRATION_RUNNER.md",
    "apps/aal-viz-live-console/README.md",
    "core/generated_artifact_registry.py",
)

LANE_RECEIPTS = (
    "out/audit/subsystem_health_dashboard_001.latest.json",
    "out/audit/continuity_namespace_migration_tooling_refresh_001.latest.json",
    "out/audit/continuity_namespace_migration_run_001.latest.json",
    "out/audit/live_console_migration_runner_posture_001.latest.json",
    "out/audit/live_projection_health_migration_artifact_001.latest.json",
    "out/audit/live_console_websocket_hardening_001.latest.json",
    "out/audit/live_console_ui_polish_001.latest.json",
)

AUTHORITY_LOCKS = {
    "sandbox_probe_gate_issued": False,
    "runtime_activation_allowed": False,
    "pipeline_activation_allowed": False,
    "canon_mutation_allowed": False,
    "mcp_exposure_allowed": False,
    "external_calls_allowed": False,
    "notion_writeback_allowed": False,
}


def _source_row(repo_root: Path, relative_path: str) -> dict[str, Any]:
    path = repo_root / relative_path
    return {
        "path": relative_path,
        "present": path.exists(),
        "surface_role": (
            "PROJECTION"
            if relative_path.endswith(".md") or relative_path.endswith(".json")
            else "EXECUTION"
        ),
    }


def build_priority2_live_console_migration_closeout_receipt(
    *, repo_root: Path
) -> dict[str, Any]:
    packet: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "status": STATUS,
        "brier_score": BRIER_SCORE,
        "slice_id": SLICE_ID,
        "summary": {
            "scope": "PRIORITY_2_LIVE_CONSOLE_AND_MIGRATION_TOOLING_CLOSEOUT",
            "documentation_only": True,
            "new_functionality": False,
            "lane_status": "CLOSED_FOR_THIS_CYCLE_ADVISORY_ONLY",
        },
        "lane_deliverables": {
            "migration_tooling": [
                "Slice62 packaging status route",
                "Slice63 migration runner scaffolding route",
            ],
            "live_console": [
                "Slice65 migration posture panel",
                "Slice66 combined posture panel",
                "Slice67 transport hardening",
                "Slice68 UI polish",
            ],
            "health_entrypoint": "Slice61 subsystem health dashboard",
            "authority_granted": False,
        },
        "current_route": {
            "start": "docs/status/SUBSYSTEM_HEALTH_DASHBOARD.md",
            "then": [
                "docs/status/CONTINUITY_NAMESPACE_MIGRATION_STATUS.md",
                "docs/status/CONTINUITY_NAMESPACE_MIGRATION_RUNNER.md",
                "apps/aal-viz-live-console/README.md",
            ],
            "closeout_receipt": DEFAULT_OUT_PATH,
        },
        "source_status_table": [_source_row(repo_root, path) for path in SOURCE_PATHS],
        "active_lane_receipts": [_source_row(repo_root, path) for path in LANE_RECEIPTS],
        "authority_locks": dict(AUTHORITY_LOCKS),
        "boundary": {
            "advisory_only": True,
            "documentation_only": True,
            "navigation_only": True,
            **dict(AUTHORITY_LOCKS),
        },
        "recommended_next_lane": (
            "Priority 2 lane closed for this cycle; reopen only with a new operator-"
            "selected dashboard, migration, or live-console card."
        ),
        "validation_plan": [
            "python Scripts/run_priority2_live_console_migration_closeout_receipt.py",
            (
                "python scripts/run_artifact_regeneration.py --artifact "
                f"{DEFAULT_OUT_PATH}"
            ),
            (
                "python -m py_compile core/priority2_live_console_migration_closeout.py "
                "Scripts/run_priority2_live_console_migration_closeout_receipt.py "
                "tests/test_priority2_live_console_migration_closeout.py"
            ),
            "git diff --check",
        ],
        "notion_closeout_text": (
            "Slice69 complete - Priority 2 Live Console and Migration Tooling lane "
            "closeout shipped; status and navigation now summarize Slice61-Slice68 "
            "through the subsystem health dashboard, continuity namespace migration "
            "status/runbook, and AAL-Viz live-console routes; no sandbox probe, runtime "
            "activation, canon mutation, MCP exposure, external calls, or autonomous "
            "writeback authorized. Brier Score: 0.10."
        ),
        "provenance": (
            "Notion Sprint 001 Hub + Loop 805 Slice 69 + "
            "Hash: priority2_live_console_migration_closeout_001.latest.json"
        ),
    }
    packet["canonical_hash"] = canonical_hash(packet)
    return packet


def write_priority2_live_console_migration_closeout_receipt(
    path: Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
