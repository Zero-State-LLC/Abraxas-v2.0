"""Script: emit deterministic temporal snapshot spine + projection bus artifacts."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id
from core.projection_bus import (
    PATCH_ID,
    build_projection_bus_envelope,
    build_projection_bus_markdown,
    write_projection_bus_envelope,
)
from core.temporal_snapshot_spine import (
    build_temporal_snapshot_index,
    write_temporal_snapshot_index,
)

_PATHS = RuntimePaths.from_env()
BUS_OUT_PATH = _PATHS.projection_bus_latest
SNAPSHOT_OUT_PATH = _PATHS.temporal_snapshot_spine_latest


def main() -> None:
    diagnostics_logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "projection_bus",
        artifact_path=BUS_OUT_PATH,
        context={"patch_id": PATCH_ID},
    )

    log_event(
        diagnostics_logger,
        "INFO",
        "projection_bus_started",
        artifact_path=BUS_OUT_PATH.as_posix(),
        snapshot_index_path=SNAPSHOT_OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    snapshot_index = build_temporal_snapshot_index(packet_id="temporal_snapshot_spine_001")
    envelope = build_projection_bus_envelope(snapshot_index, packet_id="projection_bus_001")

    write_temporal_snapshot_index(SNAPSHOT_OUT_PATH, snapshot_index)
    write_projection_bus_envelope(BUS_OUT_PATH, envelope)

    markdown_path = BUS_OUT_PATH.with_suffix(".md")
    markdown_path.write_text(
        build_projection_bus_markdown(envelope, snapshot_index),
        encoding="utf-8",
    )

    log_event(
        diagnostics_logger,
        "INFO",
        "projection_bus_completed",
        artifact_path=BUS_OUT_PATH.as_posix(),
        snapshot_index_path=SNAPSHOT_OUT_PATH.as_posix(),
        markdown_path=markdown_path.as_posix(),
        correlation_id=correlation_id,
        final_status=envelope["final_status"],
        remaining_blockers=envelope["remaining_blockers"],
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()

