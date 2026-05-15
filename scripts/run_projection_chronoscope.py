"""Script: emit deterministic projection chronoscope timeline artifacts."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id
from core.projection_chronoscope import (
    PATCH_ID,
    build_projection_chronoscope_markdown,
    build_projection_chronoscope_packet_from_artifacts,
    write_projection_chronoscope_packet,
)

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.projection_chronoscope_latest


def main() -> None:
    diagnostics_logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "projection_chronoscope",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )

    log_event(
        diagnostics_logger,
        "INFO",
        "projection_chronoscope_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    packet = build_projection_chronoscope_packet_from_artifacts(
        packet_id="projection_chronoscope_001"
    )
    write_projection_chronoscope_packet(OUT_PATH, packet)

    markdown_path = OUT_PATH.with_suffix(".md")
    markdown_path.write_text(
        build_projection_chronoscope_markdown(packet),
        encoding="utf-8",
    )

    log_event(
        diagnostics_logger,
        "INFO",
        "projection_chronoscope_completed",
        artifact_path=OUT_PATH.as_posix(),
        markdown_path=markdown_path.as_posix(),
        correlation_id=correlation_id,
        final_status=packet["final_status"],
        remaining_blockers=packet["remaining_blockers"],
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
