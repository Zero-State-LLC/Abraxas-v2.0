from __future__ import annotations

from pathlib import Path

from core.viz01_live_feed_enhancement_receipt import (
    DEFAULT_OUT_PATH,
    build_viz01_live_feed_enhancement_receipt,
    write_viz01_live_feed_enhancement_receipt,
)


def run(*, out_path: str | Path | None = None):
    packet = build_viz01_live_feed_enhancement_receipt()
    write_viz01_live_feed_enhancement_receipt(out_path or DEFAULT_OUT_PATH, packet)
    return packet
