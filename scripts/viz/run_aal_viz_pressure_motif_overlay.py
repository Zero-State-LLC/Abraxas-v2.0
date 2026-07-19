from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.aal_viz_pressure_motif_overlay import (
    build_aal_viz_pressure_motif_overlay_packet,
    write_aal_viz_pressure_motif_overlay_packet,
)
from core.config import RuntimePaths

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.aal_viz_pressure_motif_overlay_latest


def main() -> int:
    packet = build_aal_viz_pressure_motif_overlay_packet()
    write_aal_viz_pressure_motif_overlay_packet(OUT_PATH, packet)
    logging.getLogger("aal_viz_pressure_motif_overlay").info(
        "aal_viz_pressure_motif_overlay_completed final_status=%s overlay_posture=%s",
        packet["final_status"],
        packet["overlay_posture"],
    )
    print(f"{packet['final_status']} {packet['overlay_posture']}")
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    raise SystemExit(main())
