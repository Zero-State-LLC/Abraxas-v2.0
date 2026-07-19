"""Script: emit deterministic read-only transport scaffold artifacts."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id
from core.read_only_transport import (
    PATCH_ID,
    build_read_only_transport_markdown,
    build_read_only_transport_packet,
    write_read_only_transport_packet,
)

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.read_only_transport_latest


def main() -> None:
    diagnostics_logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "read_only_transport",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )

    log_event(
        diagnostics_logger,
        "INFO",
        "read_only_transport_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    packet = build_read_only_transport_packet(packet_id="read_only_transport_001")
    write_read_only_transport_packet(OUT_PATH, packet)

    markdown_path = OUT_PATH.with_suffix(".md")
    markdown_path.write_text(build_read_only_transport_markdown(packet), encoding="utf-8")

    log_event(
        diagnostics_logger,
        "INFO",
        "read_only_transport_completed",
        artifact_path=OUT_PATH.as_posix(),
        markdown_path=markdown_path.as_posix(),
        correlation_id=correlation_id,
        final_status=packet["final_status"],
        remaining_blockers=packet["remaining_blockers"],
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
