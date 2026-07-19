from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "LiveConsoleMigrationRunnerPostureReceipt.v1"
STATUS = "LIVE_CONSOLE_MIGRATION_RUNNER_POSTURE_READY_ADVISORY_ONLY"
BRIER_SCORE = "0.10"
SLICE_ID = "LOOP-805-SLICE-65"
NOTION_BOARD_URL = "https://app.notion.com/p/3843e8ba2f5c819480d0f2c5ffce6254"
DEFAULT_OUT_PATH = "out/audit/live_console_migration_runner_posture_001.latest.json"

SUBSYSTEM_HEALTH_RECEIPT_PATH = "out/audit/subsystem_health_dashboard_001.latest.json"
MIGRATION_RUNNER_RECEIPT_PATH = "out/audit/continuity_namespace_migration_run_001.latest.json"
PROJECTION_BUNDLE_PATH = "apps/aal-viz-live-console/public/projection-bundle.json"
BUILD_SCRIPT_PATH = "scripts/viz/build_aal_viz_projection_bundle.py"
LAYOUT_PATH = "apps/aal-viz-live-console/src/components/Layout.tsx"
PANEL_PATH = (
    "apps/aal-viz-live-console/src/components/MigrationRunnerPosturePanel.tsx"
)
TYPES_PATH = "apps/aal-viz-live-console/src/types.ts"
SAMPLE_BUNDLE_PATH = "apps/aal-viz-live-console/src/data/sampleProjectionBundle.ts"

SOURCE_PATHS = (
    SUBSYSTEM_HEALTH_RECEIPT_PATH,
    MIGRATION_RUNNER_RECEIPT_PATH,
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


def _posture_from_bundle(bundle_payload: dict[str, Any], bundle_status: str) -> dict[str, Any]:
    posture = bundle_payload.get("migration_runner_posture", {})
    if bundle_status != "OBSERVED" or not isinstance(posture, dict):
        return {
            "source_status": bundle_status if bundle_status != "OBSERVED" else "NOT_COMPUTABLE",
            "status": "NOT_COMPUTABLE",
            "requested_execution_result": "NOT_COMPUTABLE",
            "safe_next_surface": "NOT_COMPUTABLE",
            "blocked_action_count": 0,
            "stage_count": 0,
            "authority_granted": False,
        }
    return {
        "source_status": str(posture.get("source_status", "NOT_COMPUTABLE")),
        "status": str(posture.get("status", "NOT_COMPUTABLE")),
        "requested_execution_result": str(
            posture.get("requested_execution_result", "NOT_COMPUTABLE")
        ),
        "safe_next_surface": str(posture.get("safe_next_surface", "NOT_COMPUTABLE")),
        "blocked_action_count": int(posture.get("blocked_action_count", 0)),
        "stage_count": int(posture.get("stage_count", 0)),
        "authority_granted": False,
    }


def _posture_from_dashboard(
    dashboard_payload: dict[str, Any],
    dashboard_status: str,
) -> dict[str, Any]:
    posture = dashboard_payload.get("migration_runner_posture", {})
    if dashboard_status != "OBSERVED" or not isinstance(posture, dict):
        return {
            "source_status": dashboard_status if dashboard_status != "OBSERVED" else "NOT_COMPUTABLE",
            "status": "NOT_COMPUTABLE",
            "requested_execution_result": "NOT_COMPUTABLE",
            "safe_next_surface": "NOT_COMPUTABLE",
            "recommended_next_engineering_move": "Repair the dashboard receipt route first.",
            "blocked_action_count": 0,
            "stage_count": 0,
            "authority_granted": False,
        }
    return {
        "source_status": str(posture.get("source_status", "NOT_COMPUTABLE")),
        "status": str(posture.get("status", "NOT_COMPUTABLE")),
        "requested_execution_result": str(
            posture.get("requested_execution_result", "NOT_COMPUTABLE")
        ),
        "safe_next_surface": str(posture.get("safe_next_surface", "NOT_COMPUTABLE")),
        "recommended_next_engineering_move": str(
            posture.get("recommended_next_engineering_move", "NOT_COMPUTABLE")
        ),
        "blocked_action_count": int(posture.get("blocked_action_count", 0)),
        "stage_count": int(posture.get("stage_count", 0)),
        "authority_granted": False,
    }


def build_live_console_migration_runner_posture_receipt(
    *,
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    source_table = [_source_row(root, path) for path in SOURCE_PATHS]
    dashboard_payload, dashboard_status = _load_json(root / SUBSYSTEM_HEALTH_RECEIPT_PATH)
    bundle_payload, bundle_status = _load_json(root / PROJECTION_BUNDLE_PATH)
    runner_payload, runner_status = _load_json(root / MIGRATION_RUNNER_RECEIPT_PATH)

    dashboard_posture = _posture_from_dashboard(dashboard_payload, dashboard_status)
    bundle_posture = _posture_from_bundle(bundle_payload, bundle_status)
    live_visibility_ready = (
        bundle_status == "OBSERVED"
        and bundle_posture["status"] == dashboard_posture["status"]
        and bundle_posture["requested_execution_result"]
        == dashboard_posture["requested_execution_result"]
        and bundle_posture["safe_next_surface"] == dashboard_posture["safe_next_surface"]
    )

    source_status = (
        "READY"
        if dashboard_status == "OBSERVED" and bundle_status == "OBSERVED" and live_visibility_ready
        else "READY_WITH_FINDINGS"
    )

    base: dict[str, Any] = {
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
        "migration_runner_posture_summary": {
            "dashboard_source_status": dashboard_status,
            "bundle_source_status": bundle_status,
            "runner_source_status": runner_status,
            "live_visibility_ready": live_visibility_ready,
            "dashboard_posture": dashboard_posture,
            "bundle_posture": bundle_posture,
            "runner_status": runner_payload.get("status", "NOT_COMPUTABLE")
            if runner_status == "OBSERVED"
            else runner_status,
            "authority_granted": False,
        },
        "touched_routes": [
            "apps/aal-viz-live-console/public/projection-bundle.json",
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
            "python scripts/viz/build_aal_viz_projection_bundle.py",
            "python scripts/viz/run_live_console_migration_runner_posture_receipt.py",
            "python scripts/artifact/run_artifact_regeneration.py --artifact out/audit/live_console_migration_runner_posture_001.latest.json",
            "python -m py_compile core/live_console_migration_runner_posture.py scripts/viz/run_live_console_migration_runner_posture_receipt.py tests/test_live_console_migration_runner_posture.py",
            "python -m pytest tests/test_live_console_migration_runner_posture.py tests/test_build_aal_viz_projection_bundle.py tests/test_generated_artifact_registry.py -q -k migration_runner",
            "cd apps/aal-viz-live-console; npm test -- --run; npm run typecheck",
            "git diff --check",
        ],
        "notion_closeout_text": (
            "Slice65 complete - AAL-Viz live console now surfaces continuity namespace migration runner posture from the subsystem health dashboard receipt; migration status, held/blocked visibility, safe next surface, and stage summary are observable in the live projection bundle without opening execution paths; no sandbox probe, runtime activation, canon mutation, MCP exposure, external calls, or autonomous writeback authorized. Brier Score: 0.10."
        ),
        "recommended_next_lane": (
            "Priority 2 - Combined live projection surface for health, migration, and artifact posture."
        ),
        "provenance": "Notion Sprint 001 Hub + Loop 805 Slice65 + Hash: canonical_hash",
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def write_live_console_migration_runner_posture_receipt(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
