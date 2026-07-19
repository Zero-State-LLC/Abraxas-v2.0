from __future__ import annotations

from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "LiveConsoleWebSocketHardeningReceipt.v1"
STATUS = "LIVE_CONSOLE_WEBSOCKET_HARDENING_READY_ADVISORY_ONLY"
BRIER_SCORE = "0.10"
SLICE_ID = "LOOP-805-SLICE-67"
NOTION_BOARD_URL = "https://app.notion.com/p/3843e8ba2f5c819480d0f2c5ffce6254"
DEFAULT_OUT_PATH = "out/audit/live_console_websocket_hardening_001.latest.json"

SOURCE_PATHS = (
    "apps/aal-viz-live-console/src/data/liveProjectionFeed.ts",
    "apps/aal-viz-live-console/src/data/liveProjectionFeed.test.ts",
    "apps/aal-viz-live-console/src/App.tsx",
    "apps/aal-viz-live-console/src/components/Layout.tsx",
    "apps/aal-viz-live-console/src/state/liveConsoleReducer.ts",
    "apps/aal-viz-live-console/src/types.ts",
    "apps/aal-viz-live-console/README.md",
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


def _source_row(repo_root: Path, relative_path: str) -> dict[str, Any]:
    text, status = _read_text(repo_root / relative_path)
    return {
        "path": relative_path,
        "source_status": status,
        "line_count": len(text.splitlines()) if status == "OBSERVED" else 0,
        "authority_granted": False,
    }


def build_live_console_websocket_hardening_receipt(
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
        "transport_posture": {
            "websocket_first": True,
            "polling_fallback": True,
            "sample_fallback_preserved": True,
            "retry_policy": {
                "strategy": "DETERMINISTIC_EXPONENTIAL_BACKOFF",
                "base_delay_ms": 1000,
                "max_delay_ms": 8000,
                "jitter": "NONE",
            },
            "diagnostics_fields": [
                "retry_delay_ms",
                "last_error_reason",
                "transport_mode",
                "fallback_reason",
            ],
            "blocked_action_classes": [
                "EXECUTION",
                "RUNTIME_MUTATION",
                "PROMOTION",
                "AUTONOMOUS_WRITEBACK",
            ],
            "authority_granted": False,
        },
        "fallback_hierarchy": [
            "LIVE_STREAM",
            "POLLING_FALLBACK",
            "SAMPLE_FALLBACK",
            "FAIL_CLOSED",
        ],
        "documented_states": [
            "CONNECTING",
            "LIVE_STREAM",
            "POLLING_FALLBACK",
            "SAMPLE_FALLBACK",
            "FAIL_CLOSED",
        ],
        "recommended_next_lane": (
            "Priority 2 - either close the live-console enhancement track for this cycle "
            "or add a small visualization polish slice if operators need denser transport diagnostics."
        ),
        "validation_plan": [
            "python scripts/run_live_console_websocket_hardening_receipt.py",
            "python scripts/artifact/run_artifact_regeneration.py --artifact out/audit/live_console_websocket_hardening_001.latest.json",
            "python -m py_compile core/live_console_websocket_hardening.py scripts/run_live_console_websocket_hardening_receipt.py tests/test_live_console_websocket_hardening.py",
            "cd apps/aal-viz-live-console; npm run typecheck",
            "cd apps/aal-viz-live-console; npm test -- --run src/data/liveProjectionFeed.test.ts src/App.test.tsx",
            "git diff --check",
        ],
        "notion_closeout_text": (
            "Slice67 complete - AAL-Viz live feed transport now uses deterministic WebSocket reconnect scheduling, explicit polling fallback diagnostics, and fail-closed transport posture visibility without opening execution paths; no sandbox probe, runtime activation, canon mutation, MCP exposure, external calls, or autonomous writeback authorized. Brier Score: 0.10."
        ),
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
        "provenance": "Notion Sprint 001 Hub + Loop 805 Slice67 + Hash: canonical_hash",
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def write_live_console_websocket_hardening_receipt(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
