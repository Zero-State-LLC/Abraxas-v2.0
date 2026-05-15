"""Script: emit operator runtime console packet.

PATCH-P11-OPERATOR-RUNTIME-CONSOLE-001

Usage:
    python scripts/run_operator_runtime_console.py

Outputs:
    out/audit/operator_runtime_console_001.latest.json
    out/audit/operator_runtime_console_001.md  (Markdown summary)

Projection and operator summary only.  No runtime semantic changes.
Authority / mutation / promotion: always False.
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
    build_console_markdown,
    build_operator_console_packet,
    write_console_packet,
)

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.operator_runtime_console_latest

logger = logging.getLogger(__name__)


def main() -> None:
    diagnostics_logger = get_structured_logger(__name__)

    correlation_id = stable_correlation_id(
        "operator_runtime_console",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )

    log_event(
        diagnostics_logger,
        "INFO",
        "operator_runtime_console_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    packet = build_operator_console_packet(packet_id="operator_runtime_console_001")

    write_console_packet(OUT_PATH, packet)

    # Markdown summary
    md_path = OUT_PATH.with_suffix(".md")
    md_content = build_console_markdown(packet)
    md_path.write_text(md_content, encoding="utf-8")

    log_event(
        diagnostics_logger,
        "INFO",
        "operator_runtime_console_completed",
        artifact_path=OUT_PATH.as_posix(),
        markdown_path=md_path.as_posix(),
        correlation_id=correlation_id,
        final_status=packet["final_status"],
        remaining_blockers=packet["remaining_blockers"],
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
