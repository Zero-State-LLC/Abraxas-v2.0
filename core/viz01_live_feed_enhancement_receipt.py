from __future__ import annotations

from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "VIZ01LiveFeedEnhancementReceipt.v1"
SLICE_ID = "LOOP-805-SLICE-52"
STATUS = "VIZ01_LIVE_FEED_ENHANCEMENT_READY_ADVISORY_ONLY"
BRIER_SCORE = "0.10"
DEFAULT_OUT_PATH = "out/audit/viz01_live_feed_enhancement_receipt_001.latest.json"

_AUTHORITY_LOCKS = {
    "canon_mutation": False,
    "external_calls": False,
    "github_writeback": False,
    "mcp_exposure": False,
    "notion_writeback": False,
    "production_activation": False,
    "runtime_activation": False,
    "runtime_mutation": False,
    "sandbox_probe_execution": False,
    "secret_capture": False,
}


def build_viz01_live_feed_enhancement_receipt() -> dict[str, Any]:
    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "slice_id": SLICE_ID,
        "status": STATUS,
        "brier_score": BRIER_SCORE,
        "advisory_only": True,
        "projection_only": True,
        "authority_locks": _AUTHORITY_LOCKS,
        "implemented_surfaces": [
            "apps/aal-viz-live-console/src/data/liveProjectionFeed.ts",
            "apps/aal-viz-live-console/src/App.tsx",
            "apps/aal-viz-live-console/src/state/liveConsoleReducer.ts",
            "apps/aal-viz-live-console/src/components/Layout.tsx",
            "apps/aal-viz-live-console/src/components/StatusPills.tsx",
        ],
        "public_interfaces": {
            "optional_websocket_env": "VITE_AAL_VIZ_WS_URL",
            "optional_poll_interval_env": "VITE_AAL_VIZ_POLL_MS",
            "default_poll_ms": 5000,
            "connection_states": [
                "CONNECTING",
                "LIVE_STREAM",
                "POLLING_FALLBACK",
                "SAMPLE_FALLBACK",
                "FAIL_CLOSED",
            ],
        },
        "boundary": {
            "sandbox_gate_issue": "#892",
            "sandbox_gate_phrase": "ORACLE_SANDBOX_PROBE_GATE_CONFIRMED",
            "sandbox_gate_issued": False,
            "scope_note": (
                "VIZ-01 adds read-only live projection feed handling and deterministic "
                "fallbacks only. It does not run sandbox probes, call external "
                "oracles, mutate canon/runtime, expose MCP, capture secrets, or "
                "write back to GitHub/Notion."
            ),
        },
        "validation_plan": [
            "npm test -- --run",
            "npm run typecheck",
            "python scripts/viz/run_viz01_live_feed_enhancement_receipt.py",
            "python -m py_compile core/viz01_live_feed_enhancement_receipt.py "
            "scripts/viz/run_viz01_live_feed_enhancement_receipt.py",
            "git diff --check",
        ],
        "provenance": (
            "Notion Sprint 001 Hub + Loop 805 Slice 52 + "
            "VIZ-01 Live Projection Feed Enhancement"
        ),
    }
    return {**packet_base, "canonical_hash": canonical_hash(packet_base)}


def write_viz01_live_feed_enhancement_receipt(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
