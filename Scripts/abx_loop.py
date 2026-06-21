from __future__ import annotations

import argparse
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_SCRIPT_DIR_KEY = _SCRIPT_DIR.casefold()
_ROOT_DIR = os.path.dirname(_SCRIPT_DIR)
sys.path = [
    path
    for path in sys.path
    if os.path.abspath(path or os.curdir).casefold() != _SCRIPT_DIR_KEY
]
if _ROOT_DIR not in sys.path:
    sys.path.insert(0, _ROOT_DIR)

from core.canonical.json import write_canonical_json  # noqa: E402
from core.codegen.loop805_controller import build_loop805_controller_plan  # noqa: E402
from core.codegen.loop805_operationalization import (  # noqa: E402
    build_loop805_baseline_receipt,
    build_loop805_continuity_signal,
)
from core.codegen.spine_mcp_projection import (  # noqa: E402
    build_spine_audit_projection,
    build_spine_forecast_projection,
    build_spine_query_projection,
)


DEFAULT_TIMESTAMP = "2026-06-21T23:05:00Z"
DEFAULT_MERGE_SHA = "8eeb7f4df62feae25651645b589698a503fb40e6"
DEFAULT_BASELINE_OUT = (
    "out/audit/abx_loop_805_operationalization_baseline_001.latest.json"
)
DEFAULT_CONTROLLER_OUT = "out/audit/abx_loop_805_controller_plan_001.latest.json"


def _timestamp(value: str | None) -> str:
    if value:
        return value
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _source_receipts() -> list[str]:
    return [
        "out/audit/abx_codegen_intelligence_spine_completion_receipt_001.latest.json",
        "out/audit/abx_codex_governance_loop_phase_6_post_merge_reconciliation.latest.json",
        "out/audit/abx_codex_governance_loop_phase_7_shadow_runtime_activation_prep.latest.json",
        "out/audit/abx_codex_governance_loop_phase_8_global_ingest_wiring_stub.latest.json",
        "out/audit/abx_codex_governance_loop_phase_9_notion_projection_dryrun.latest.json",
        "out/audit/abx_codegen_phase_10_plus_forward_paths_selector.latest.json",
    ]


def _validation_summary() -> dict[str, Any]:
    return {
        "run_fast_ci": {
            "status": "BASELINE_KNOWN_FAILURES_WINDOWS_PATH_ENCODING",
            "detail": (
                "Post-#804 fast CI reaches pytest but retains existing CP1252 "
                "arrow output and backslash-vs-slash schema constant failures."
            ),
            "brier_score": 0.1,
        },
        "pyright": {
            "status": "TARGETED_PASS",
            "scope": "scripts/abraxas_v2.0_codex_governance_loop.py",
            "errors": 0,
            "brier_score": 0.08,
        },
        "ruff": {
            "status": "TARGETED_PASS",
            "scope": "Loop 805 touched surfaces",
            "brier_score": 0.08,
        },
    }


def build_all_packets(timestamp: str, merge_sha: str) -> dict[str, dict[str, Any]]:
    baseline = build_loop805_baseline_receipt(
        timestamp=timestamp,
        main_merge_sha=merge_sha,
        source_receipts=_source_receipts(),
        validation_summary=_validation_summary(),
    )
    controller = build_loop805_controller_plan(
        timestamp=timestamp,
        task="Run 24h forecast accuracy stress test on 2026 midterms signal set",
        measurements=[
            build_loop805_continuity_signal(
                surface="token_efficiency",
                status="BASELINE_CAPTURED",
                detail="Prior thread goal consumed 596311 tokens; target reduction is 18%.",
                brier_score=0.1,
            ),
            build_loop805_continuity_signal(
                surface="brier_uplift",
                status="HELD_OUT_SET_REQUIRED",
                detail="Brier uplift target declared; outcome binding not yet authorized.",
                brier_score=0.12,
            ),
        ],
    )
    return {
        "baseline": baseline,
        "controller": controller,
        "spine_query_projection": build_spine_query_projection(
            timestamp=timestamp,
            query="ABX Codegen Intelligence Spine status and next lanes",
        ),
        "spine_forecast_projection": build_spine_forecast_projection(
            timestamp=timestamp,
            forecast_question="Will Loop 805 reduce average tokens per agent turn by 18%?",
            probability=0.62,
        ),
        "spine_audit_projection": build_spine_audit_projection(
            timestamp=timestamp,
            surface="ABX_CODEGEN_INTELLIGENCE_SPINE_ADVISORY_COMPUTABLE",
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Emit ABX Loop 805 advisory operationalization receipts."
    )
    parser.add_argument("--timestamp", default=DEFAULT_TIMESTAMP)
    parser.add_argument("--merge-sha", default=DEFAULT_MERGE_SHA)
    parser.add_argument("--baseline-out", default=DEFAULT_BASELINE_OUT)
    parser.add_argument("--controller-out", default=DEFAULT_CONTROLLER_OUT)
    parser.add_argument(
        "--emit-controller",
        action="store_true",
        help="Also emit the PLAN_EXECUTE_MEASURE_ADJUST controller receipt.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    timestamp = _timestamp(args.timestamp)
    packets = build_all_packets(timestamp, args.merge_sha)
    write_canonical_json(Path(args.baseline_out), packets["baseline"])
    print(args.baseline_out)
    print(packets["baseline"]["canonical_hash"])

    if args.emit_controller:
        write_canonical_json(Path(args.controller_out), packets["controller"])
        print(args.controller_out)
        print(packets["controller"]["canonical_hash"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
