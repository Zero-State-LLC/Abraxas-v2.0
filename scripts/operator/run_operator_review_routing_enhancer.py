"""Script: emit deterministic P30 operator review routing enhancer artifacts."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.config import RuntimePaths
from core.operator_review_routing_enhancer import (
    build_operator_review_routing_enhancer_packet,
    write_operator_review_routing_enhancer_packet,
)

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.operator_review_routing_enhancer_latest


def main() -> None:
    packet = build_operator_review_routing_enhancer_packet()
    write_operator_review_routing_enhancer_packet(OUT_PATH, packet)
    logging.info(
        "operator_review_routing_enhancer_completed final_status=%s routing_posture=%s",
        packet["final_status"],
        packet["routing_posture"],
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
