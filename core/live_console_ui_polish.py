from __future__ import annotations

from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "LiveConsoleUiPolishReceipt.v1"
STATUS = "LIVE_CONSOLE_UI_POLISH_READY_ADVISORY_ONLY"
BRIER_SCORE = "0.10"
SLICE_ID = "LOOP-805-SLICE-68"
NOTION_BOARD_URL = "https://app.notion.com/p/3843e8ba2f5c819480d0f2c5ffce6254"
DEFAULT_OUT_PATH = "out/audit/live_console_ui_polish_001.latest.json"

SOURCE_PATHS = (
    "apps/aal-viz-live-console/src/components/StatusPills.tsx",
    "apps/aal-viz-live-console/src/components/Layout.tsx",
    "apps/aal-viz-live-console/src/components/MigrationRunnerPosturePanel.tsx",
    "apps/aal-viz-live-console/src/components/CombinedHealthMigrationArtifactPanel.tsx",
    "apps/aal-viz-live-console/src/styles.css",
    "apps/aal-viz-live-console/README.md",
    "core/generated_artifact_registry.py",
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
        "surface_role": "PROJECTION" if relative_path.endswith(".md") else "EXECUTION",
    }


def build_live_console_ui_polish_receipt(*, repo_root: Path) -> dict[str, Any]:
    packet: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "status": STATUS,
        "brier_score": BRIER_SCORE,
        "slice_id": SLICE_ID,
        "summary": {
            "scope": "LIVE_CONSOLE_BADGE_AND_POSTURE_POLISH",
            "presentational_only": True,
            "new_data_fields": False,
            "new_execution_paths": False,
        },
        "ui_polish_focus": {
            "shared_presentational_surface": "apps/aal-viz-live-console/src/components/StatusPills.tsx",
            "touched_panels": [
                "MigrationRunnerPosturePanel",
                "CombinedHealthMigrationArtifactPanel",
                "Layout feed diagnostics",
            ],
            "standardized_elements": [
                "badge sizing",
                "badge casing",
                "advisory note treatment",
                "fail-closed posture treatment",
                "diagnostic spacing",
            ],
            "authority_granted": False,
        },
        "source_status_table": [_source_row(repo_root, path) for path in SOURCE_PATHS],
        "authority_locks": dict(AUTHORITY_LOCKS),
        "boundary": {
            "advisory_only": True,
            "presentation_only": True,
            "no_logic_changes_intended": True,
            **dict(AUTHORITY_LOCKS),
        },
        "validation_plan": [
            "pnpm/vitest targeted component smoke",
            f"python scripts/artifact/run_artifact_regeneration.py --artifact {DEFAULT_OUT_PATH}",
            "tsc --noEmit",
            "git diff --check",
        ],
        "notion_closeout_text": (
            "Slice68 complete - Live Console UI polish shipped; badge and posture treatment is now "
            "more consistent across migration, combined posture, and feed diagnostics while staying "
            "advisory-only and read-only. No sandbox probe, runtime activation, canon mutation, MCP "
            "exposure, external calls, or autonomous writeback authorized. Brier Score: 0.10."
        ),
        "provenance": (
            "Notion Sprint 001 Hub + Loop 805 Slice 68 + "
            "Hash: live_console_ui_polish_001.latest.json"
        ),
    }
    packet["canonical_hash"] = canonical_hash(packet)
    return packet


def write_live_console_ui_polish_receipt(path: Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)

