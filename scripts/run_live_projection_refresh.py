"""Script: emit live projection refresh loop packet.

PATCH-P14-LIVE-PROJECTION-REFRESH-LOOP-001

Usage:
    python scripts/run_live_projection_refresh.py

Outputs:
    out/projections/live_projection_refresh_001.latest.json
    out/projections/live_projection_refresh_001.md  (Markdown summary)

Projection and operator summary only.  No runtime semantic changes.
Authority / mutation / promotion / inference_authority: always False.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.live_projection_refresh import (
    PATCH_ID,
    build_live_projection_refresh_packet,
    build_refresh_markdown,
    write_live_projection_refresh_packet,
)
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

OUT_DIR = Path("out/projections")
OUT_PATH = OUT_DIR / "live_projection_refresh_001.latest.json"

logger = logging.getLogger(__name__)


def main() -> None:
    diagnostics_logger = get_structured_logger(__name__)

    correlation_id = stable_correlation_id(
        "live_projection_refresh",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )

    log_event(
        diagnostics_logger,
        "INFO",
        "live_projection_refresh_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    packet = build_live_projection_refresh_packet(
        packet_id="live_projection_refresh_001",
        max_cycles=1,
        refresh_reasons=["scheduled_advisory"],
        timestamps=["live_projection_refresh_001_ts_0"],
        durations_ns=[0],
        advisory_flags=[],
    )

    write_live_projection_refresh_packet(OUT_PATH, packet)

    # Markdown summary
    md_path = OUT_PATH.with_suffix(".md")
    md_content = build_refresh_markdown(packet)
    md_path.write_text(md_content, encoding="utf-8")

    log_event(
        diagnostics_logger,
        "INFO",
        "live_projection_refresh_completed",
        artifact_path=OUT_PATH.as_posix(),
        markdown_path=md_path.as_posix(),
        correlation_id=correlation_id,
        final_status=packet["final_status"],
        remaining_blockers=packet["remaining_blockers"],
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
