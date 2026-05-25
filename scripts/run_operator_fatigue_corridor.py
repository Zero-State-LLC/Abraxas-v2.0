from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import RuntimePaths
from core.operator_fatigue_corridor import (
    build_operator_fatigue_corridor_packet,
    write_operator_fatigue_corridor_packet,
)

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.operator_fatigue_corridor_latest


def main() -> int:
    packet = build_operator_fatigue_corridor_packet()
    write_operator_fatigue_corridor_packet(OUT_PATH, packet)
    logging.getLogger("operator_fatigue_corridor").info(
        "operator_fatigue_corridor_completed final_status=%s corridor_status=%s",
        packet["final_status"],
        packet["corridor_status"],
    )
    print(f"{packet['final_status']} {packet['corridor_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
