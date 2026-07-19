from __future__ import annotations

from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "LiveConsoleTransportDiagnosticsVisibilityReceipt.v1"
STATUS = "LIVE_CONSOLE_TRANSPORT_DIAGNOSTICS_VISIBILITY_READY_ADVISORY_ONLY"
BRIER_SCORE = "0.10"
SLICE_ID = "LOOP-805-PRIORITY2-LIVE-CONSOLE-TRANSPORT-DIAGNOSTICS"
NOTION_BOARD_URL = "https://app.notion.com/p/3843e8ba2f5c819480d0f2c5ffce6254"
DEFAULT_OUT_PATH = "out/audit/live_console_transport_diagnostics_visibility_001.latest.json"

SOURCE_PATHS = (
    "apps/aal-viz-live-console/src/components/TransportDiagnosticsPanel.tsx",
    "apps/aal-viz-live-console/src/components/TransportDiagnosticsPanel.test.tsx",
    "apps/aal-viz-live-console/src/components/Layout.tsx",
    "apps/aal-viz-live-console/src/App.test.tsx",
    "apps/aal-viz-live-console/src/state/liveConsoleReducer.ts",
    "apps/aal-viz-live-console/src/data/liveProjectionFeed.ts",
    "apps/aal-viz-live-console/src/types.ts",
    "out/audit/live_console_websocket_hardening_001.latest.json",
    "out/audit/live_console_migration_preflight_projection_001.latest.json",
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
    "scheduler_mutation": False,
    "socket_control_authority": False,
}


def _read_text(path: Path) -> tuple[str, str]:
    try:
        return path.read_text(encoding="utf-8"), "OBSERVED"
    except FileNotFoundError:
        return "", "MISSING"
    except OSError:
        return "", "NOT_COMPUTABLE"


def _source_row(repo_root: Path, relative_path: str) -> dict[str, Any]:
    text, status = _read_text(repo_root / relative_path)
    return {
        "path": relative_path,
        "source_status": status,
        "line_count": len(text.splitlines()) if status == "OBSERVED" else 0,
        "authority_granted": False,
    }


def build_live_console_transport_diagnostics_visibility_receipt(
    *,
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    source_table = [_source_row(root, path) for path in SOURCE_PATHS]
    observed_count = sum(1 for row in source_table if row["source_status"] == "OBSERVED")
    base = {
        "artifact_type": ARTIFACT_TYPE,
        "slice_id": SLICE_ID,
        "status": STATUS,
        "brier_score": BRIER_SCORE,
        "advisory_only": True,
        "projection_only": True,
        "notion_board_url": NOTION_BOARD_URL,
        "authority_locks": AUTHORITY_LOCKS,
        "source_status": "READY" if observed_count == len(source_table) else "READY_WITH_FINDINGS",
        "source_table": source_table,
        "diagnostic_surface": {
            "panel": "TransportDiagnosticsPanel",
            "source_fields": [
                "connection_status",
                "connection_transport_mode",
                "connection_reconnect_attempts",
                "connection_retry_delay_ms",
                "connection_last_error_reason",
                "connection_fallback_reason",
                "connection_last_updated",
            ],
            "display_only": True,
            "socket_control_authority": False,
            "polling_cadence_authority": False,
            "reconnect_trigger_authority": False,
            "authority_granted": False,
        },
        "blocked_action_classes": [
            "OPEN_SOCKET",
            "CHANGE_POLLING_CADENCE",
            "TRIGGER_RECONNECT",
            "RUNTIME_MUTATION",
            "AUTONOMOUS_WRITEBACK",
        ],
        "recommended_next_lane": (
            "Return to the Notion engineering board for the next active card; "
            "live-console transport diagnostics are now display-only and PR-ready."
        ),
        "validation_plan": [
            "python scripts/viz/run_live_console_transport_diagnostics_visibility_receipt.py",
            "python scripts/artifact/run_artifact_regeneration.py --artifact out/audit/live_console_transport_diagnostics_visibility_001.latest.json",
            "python -m py_compile core/live_console_transport_diagnostics_visibility.py scripts/viz/run_live_console_transport_diagnostics_visibility_receipt.py tests/test_live_console_transport_diagnostics_visibility.py",
            "cd apps/aal-viz-live-console; npm test -- --run src/components/TransportDiagnosticsPanel.test.tsx src/App.test.tsx",
            "git diff --check",
        ],
        "notion_closeout_text": (
            "Priority 2 live-console transport diagnostics visibility shipped; "
            "the existing feed transport fields are now exposed through a dedicated display-only panel "
            "without opening socket control, polling cadence changes, reconnect triggers, runtime activation, "
            "canon mutation, scheduler mutation, external calls, or autonomous writeback. Brier Score: 0.10."
        ),
        "boundary": {
            "canon_mutation": False,
            "external_calls": False,
            "github_writeback": False,
            "mcp_exposure": False,
            "notion_writeback": False,
            "runtime_activation": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
            "socket_control_authority": False,
        },
        "provenance": "Notion Engineering Board next recommended live-console projection lane + Hash: canonical_hash",
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def write_live_console_transport_diagnostics_visibility_receipt(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
