from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "LiveConsoleMigrationPreflightProjectionReceipt.v1"
STATUS = "LIVE_CONSOLE_MIGRATION_PREFLIGHT_PROJECTION_READY_ADVISORY_ONLY"
BRIER_SCORE = "0.10"
SLICE_ID = "LOOP-805-PRIORITY2-LIVE-CONSOLE-PREFLIGHT-PROJECTION"
NOTION_BOARD_URL = "https://app.notion.com/p/3843e8ba2f5c819480d0f2c5ffce6254"
DEFAULT_OUT_PATH = "out/audit/live_console_migration_preflight_projection_001.latest.json"

PREFLIGHT_RECEIPT_PATH = (
    "out/audit/continuity_namespace_migration_preflight_001.latest.json"
)
PROJECTION_BUNDLE_PATH = "apps/aal-viz-live-console/public/projection-bundle.json"
BUILD_SCRIPT_PATH = "scripts/viz/build_aal_viz_projection_bundle.py"
LAYOUT_PATH = "apps/aal-viz-live-console/src/components/Layout.tsx"
PANEL_PATH = (
    "apps/aal-viz-live-console/src/components/MigrationPreflightPosturePanel.tsx"
)
TYPES_PATH = "apps/aal-viz-live-console/src/types.ts"
SAMPLE_BUNDLE_PATH = "apps/aal-viz-live-console/src/data/sampleProjectionBundle.ts"

SOURCE_PATHS = (
    PREFLIGHT_RECEIPT_PATH,
    PROJECTION_BUNDLE_PATH,
    BUILD_SCRIPT_PATH,
    LAYOUT_PATH,
    PANEL_PATH,
    TYPES_PATH,
    SAMPLE_BUNDLE_PATH,
    "core/generated_artifact_registry.py",
)

AUTHORITY_LOCKS = {
    "alias_materialization": False,
    "canon_mutation": False,
    "execution_authority": False,
    "external_calls": False,
    "github_writeback": False,
    "mcp_exposure": False,
    "notion_writeback": False,
    "path_rename_authority": False,
    "production_activation": False,
    "runtime_activation": False,
    "runtime_mutation": False,
    "scheduler_mutation": False,
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


def _preflight_projection_from_bundle(
    bundle_payload: dict[str, Any],
    bundle_status: str,
) -> dict[str, Any]:
    posture = bundle_payload.get("migration_preflight_posture", {})
    if bundle_status != "OBSERVED" or not isinstance(posture, dict):
        return {
            "source_status": bundle_status
            if bundle_status != "OBSERVED"
            else "NOT_COMPUTABLE",
            "status": "NOT_COMPUTABLE",
            "check_count": 0,
            "pass_count": 0,
            "held_count": 0,
            "authority_granted": False,
        }
    return {
        "source_status": str(posture.get("source_status", "NOT_COMPUTABLE")),
        "status": str(posture.get("status", "NOT_COMPUTABLE")),
        "check_count": int(posture.get("check_count", 0)),
        "pass_count": int(posture.get("pass_count", 0)),
        "held_count": int(posture.get("held_count", 0)),
        "authority_granted": False,
    }


def _preflight_summary(
    preflight_payload: dict[str, Any],
    preflight_status: str,
) -> dict[str, Any]:
    summary = preflight_payload.get("preflight_summary", {})
    if preflight_status != "OBSERVED" or not isinstance(summary, dict):
        return {
            "source_status": preflight_status
            if preflight_status != "OBSERVED"
            else "NOT_COMPUTABLE",
            "status": "NOT_COMPUTABLE",
            "check_count": 0,
            "pass_count": 0,
            "held_count": 0,
            "authority_granted": False,
        }
    return {
        "source_status": str(preflight_payload.get("source_status", "NOT_COMPUTABLE")),
        "status": str(preflight_payload.get("status", "NOT_COMPUTABLE")),
        "check_count": int(summary.get("check_count", 0)),
        "pass_count": int(summary.get("pass_count", 0)),
        "held_count": int(summary.get("held_count", 0)),
        "authority_granted": False,
    }


def build_live_console_migration_preflight_projection_receipt(
    *,
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    source_table = [_source_row(root, path) for path in SOURCE_PATHS]
    preflight_payload, preflight_status = _load_json(root / PREFLIGHT_RECEIPT_PATH)
    bundle_payload, bundle_status = _load_json(root / PROJECTION_BUNDLE_PATH)
    preflight_summary = _preflight_summary(preflight_payload, preflight_status)
    bundle_projection = _preflight_projection_from_bundle(bundle_payload, bundle_status)

    live_visibility_ready = (
        preflight_status == "OBSERVED"
        and bundle_status == "OBSERVED"
        and bundle_projection["status"] == preflight_summary["status"]
        and bundle_projection["check_count"] == preflight_summary["check_count"]
        and bundle_projection["pass_count"] == preflight_summary["pass_count"]
        and bundle_projection["held_count"] == preflight_summary["held_count"]
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
        "source_status": "READY" if live_visibility_ready else "READY_WITH_FINDINGS",
        "source_table": source_table,
        "canonical_source_path": PREFLIGHT_RECEIPT_PATH,
        "projection_bundle_path": PROJECTION_BUNDLE_PATH,
        "migration_preflight_projection_summary": {
            "preflight_source_status": preflight_status,
            "bundle_source_status": bundle_status,
            "live_visibility_ready": live_visibility_ready,
            "preflight_summary": preflight_summary,
            "bundle_projection": bundle_projection,
            "authority_granted": False,
        },
        "touched_routes": [
            PROJECTION_BUNDLE_PATH,
            BUILD_SCRIPT_PATH,
            LAYOUT_PATH,
            PANEL_PATH,
            TYPES_PATH,
            SAMPLE_BUNDLE_PATH,
            "tests/test_build_aal_viz_projection_bundle.py",
        ],
        "boundary": {
            "alias_materialization": False,
            "canon_mutation": False,
            "external_calls": False,
            "github_writeback": False,
            "mcp_exposure": False,
            "notion_writeback": False,
            "runtime_activation": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
        },
        "validation_plan": [
            "python scripts/viz/build_aal_viz_projection_bundle.py",
            "python scripts/viz/run_live_console_migration_preflight_projection_receipt.py",
            "python scripts/artifact/run_artifact_regeneration.py --artifact out/audit/live_console_migration_preflight_projection_001.latest.json",
            "python -m py_compile core/live_console_migration_preflight_projection.py scripts/viz/run_live_console_migration_preflight_projection_receipt.py tests/test_live_console_migration_preflight_projection.py",
            "python -m pytest tests/test_build_aal_viz_projection_bundle.py tests/test_live_console_migration_preflight_projection.py tests/test_generated_artifact_registry.py -q -k 'migration_preflight or live_console_migration_preflight_projection'",
            "cd apps/aal-viz-live-console; npm test -- --run MigrationPreflightPosturePanel; npm run typecheck",
            "git diff --check",
        ],
        "notion_closeout_text": (
            "Priority 2 live-console preflight projection shipped; the AAL-Viz projection bundle now exposes the continuity namespace migration preflight counts, held checks, blocked authority sample, and safe next engineering move as display-only posture; no alias materialization, path rename, runtime activation, canon mutation, queue/scheduler mutation, external calls, or autonomous writeback authorized. Brier Score: 0.10."
        ),
        "recommended_next_lane": (
            "Priority 2 live console - continue with the next read-only projection or WebSocket diagnostic surface."
        ),
        "provenance": "Notion Engineering Board Priority 2 Card 2 + Hash: canonical_hash",
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def write_live_console_migration_preflight_projection_receipt(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
