from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.config import RuntimePaths
from core.operator_load_seasonality_surface import (
    build_operator_load_seasonality_surface_packet,
    write_operator_load_seasonality_surface_packet,
)

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.operator_load_seasonality_latest


def main() -> int:
    packet = build_operator_load_seasonality_surface_packet()
    write_operator_load_seasonality_surface_packet(OUT_PATH, packet)
    logging.getLogger("operator_load_seasonality_surface").info(
        "operator_load_seasonality_surface_completed final_status=%s seasonality_posture=%s",
        packet["final_status"],
        packet["seasonality_posture"],
    )
    print(f"final_status={packet['final_status']} seasonality_posture={packet['seasonality_posture']}")
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    raise SystemExit(main())
