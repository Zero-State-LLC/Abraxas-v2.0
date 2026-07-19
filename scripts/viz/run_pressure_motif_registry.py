from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.config import RuntimePaths
from core.pressure_motif_registry import (
    build_pressure_motif_registry_packet,
    write_pressure_motif_registry_packet,
)

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.pressure_motif_registry_latest


def main() -> int:
    packet = build_pressure_motif_registry_packet()
    write_pressure_motif_registry_packet(OUT_PATH, packet)
    logging.getLogger("pressure_motif_registry").info(
        "pressure_motif_registry_completed final_status=%s registry_posture=%s",
        packet["final_status"],
        packet["registry_posture"],
    )
    print(f"final_status={packet['final_status']} registry_posture={packet['registry_posture']}")
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    raise SystemExit(main())
