"""Script: emit deterministic AAL-Viz graph render packet artifacts."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.aal_viz_graph_render_packet import (
    PATCH_ID,
    build_aal_viz_graph_render_markdown,
    build_aal_viz_graph_render_packet,
    write_aal_viz_graph_render_packet,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.aal_viz_graph_render_packet_latest


def main() -> None:
    diagnostics_logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "aal_viz_graph_render_packet",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )

    log_event(
        diagnostics_logger,
        "INFO",
        "aal_viz_graph_render_packet_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    packet = build_aal_viz_graph_render_packet(packet_id="aal_viz_graph_render_packet_001")
    write_aal_viz_graph_render_packet(OUT_PATH, packet)

    markdown_path = OUT_PATH.with_suffix(".md")
    markdown_path.write_text(
        build_aal_viz_graph_render_markdown(packet),
        encoding="utf-8",
    )

    log_event(
        diagnostics_logger,
        "INFO",
        "aal_viz_graph_render_packet_completed",
        artifact_path=OUT_PATH.as_posix(),
        markdown_path=markdown_path.as_posix(),
        correlation_id=correlation_id,
        final_status=packet["final_status"],
        remaining_blockers=packet["remaining_blockers"],
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
