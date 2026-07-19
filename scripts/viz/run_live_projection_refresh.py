"""Script: emit deterministic live projection refresh artifacts."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.config import RuntimePaths
from core.live_projection_refresh import (
    PATCH_ID,
    build_live_projection_refresh_packet,
    build_refresh_markdown,
    write_live_projection_refresh_packet,
)

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.live_projection_refresh_latest


def main() -> None:
    packet = build_live_projection_refresh_packet(
        packet_id="live_projection_refresh_001",
        max_cycles=1,
        refresh_reasons=["scheduled_advisory"],
        timestamps=["live_projection_refresh_001_ts_0"],
        durations_ns=[0],
    )
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    write_live_projection_refresh_packet(OUT_PATH, packet)

    markdown_path = OUT_PATH.with_suffix(".md")
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(build_refresh_markdown(packet), encoding="utf-8")

    print(
        f"{PATCH_ID} wrote {OUT_PATH.as_posix()} and {markdown_path.as_posix()}",
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
