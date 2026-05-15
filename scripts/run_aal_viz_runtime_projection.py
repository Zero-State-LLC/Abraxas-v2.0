"""Script: emit AAL-Viz runtime projection packet.

PATCH-P13-AAL-VIZ-RUNTIME-PROJECTION-INTEGRATION-001

Usage:
    python scripts/run_aal_viz_runtime_projection.py

Outputs:
    out/projections/aal_viz_runtime_projection_001.latest.json
    out/projections/aal_viz_runtime_projection_001.md  (Markdown summary)

Projection and operator summary only.  No runtime semantic changes.
Authority / mutation / promotion / inference_authority: always False.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.aal_viz_runtime_projection import (
    PATCH_ID,
    build_projection_markdown,
    build_runtime_projection_packet,
    write_runtime_projection_packet,
)
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

OUT_DIR = Path("out/projections")
OUT_PATH = OUT_DIR / "aal_viz_runtime_projection_001.latest.json"

logger = logging.getLogger(__name__)


def main() -> None:
    diagnostics_logger = get_structured_logger(__name__)

    correlation_id = stable_correlation_id(
        "aal_viz_runtime_projection",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )

    log_event(
        diagnostics_logger,
        "INFO",
        "aal_viz_runtime_projection_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    packet = build_runtime_projection_packet(packet_id="aal_viz_runtime_projection_001")

    write_runtime_projection_packet(OUT_PATH, packet)

    # Markdown summary
    md_path = OUT_PATH.with_suffix(".md")
    md_content = build_projection_markdown(packet)
    md_path.write_text(md_content, encoding="utf-8")

    log_event(
        diagnostics_logger,
        "INFO",
        "aal_viz_runtime_projection_completed",
        artifact_path=OUT_PATH.as_posix(),
        markdown_path=md_path.as_posix(),
        correlation_id=correlation_id,
        final_status=packet["final_status"],
        remaining_blockers=packet["remaining_blockers"],
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
