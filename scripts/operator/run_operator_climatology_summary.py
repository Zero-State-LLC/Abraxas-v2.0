from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.config import RuntimePaths
from core.operator_climatology_summary import (
    build_operator_climatology_summary_packet,
    write_operator_climatology_summary_packet,
)

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.operator_climatology_summary_latest


def main() -> int:
    packet = build_operator_climatology_summary_packet()
    write_operator_climatology_summary_packet(OUT_PATH, packet)
    logging.getLogger("operator_climatology_summary").info(
        "operator_climatology_summary_completed final_status=%s climatology_posture=%s",
        packet["final_status"],
        packet["climatology_posture"],
    )
    print(f"{packet['final_status']} {packet['climatology_posture']}")
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    raise SystemExit(main())
