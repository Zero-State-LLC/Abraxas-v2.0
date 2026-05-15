"""Script: emit operator runtime console packet.

PATCH-P11-OPERATOR-RUNTIME-CONSOLE-001

Usage:
    python scripts/run_operator_runtime_console.py

Outputs:
    out/audit/operator_runtime_console_001.latest.json
    out/audit/operator_runtime_console_001.md   (optional Markdown summary)

Projection-only.  Advisory-only.  No authority or mutation side effects.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id
from core.operator_runtime_console import (
    PATCH_ID,
    build_markdown_summary,
    build_operator_runtime_console_packet,
    write_operator_runtime_console_packet,
)

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.operator_runtime_console_latest
MD_PATH = _PATHS.audit_dir / "operator_runtime_console_001.md"

PACKET_ID = "operator_runtime_console_001"

logger = logging.getLogger(__name__)


def main() -> None:
    diagnostics_logger = get_structured_logger(__name__)

    correlation_id = stable_correlation_id(
        "run_operator_runtime_console",
        artifact_path=OUT_PATH,
        context={"packet_id": PACKET_ID},
    )

    log_event(
        diagnostics_logger,
        "INFO",
        "operator_runtime_console_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
        patch_id=PATCH_ID,
    )

    packet = build_operator_runtime_console_packet(
        packet_id=PACKET_ID,
        runtime_profile_path=_PATHS.runtime_performance_profile_latest,
        benchmark_path=_PATHS.runtime_benchmark_latest,
        stabilization_path=_PATHS.audit_dir / "stabilization_release_readiness_001.latest.json",
        governance_freeze_path=_PATHS.audit_dir / "governance_freeze_baseline_001.latest.json",
    )

    written_path = write_operator_runtime_console_packet(OUT_PATH, packet)

    # Emit optional Markdown summary
    md_text = build_markdown_summary(packet)
    MD_PATH.parent.mkdir(parents=True, exist_ok=True)
    MD_PATH.write_text(md_text, encoding="utf-8")

    log_event(
        diagnostics_logger,
        "INFO",
        "operator_runtime_console_completed",
        artifact_path=written_path.as_posix(),
        correlation_id=correlation_id,
        final_posture=packet["final_posture"],
        remaining_blockers=packet["remaining_blockers"],
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
