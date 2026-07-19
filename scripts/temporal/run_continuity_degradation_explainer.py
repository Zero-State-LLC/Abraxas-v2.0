from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.continuity_degradation_explainer import (
    build_continuity_degradation_explainer_packet,
    write_continuity_degradation_explainer_packet,
)
from core.config import RuntimePaths

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.continuity_degradation_explainer_latest


def main() -> None:
    packet = build_continuity_degradation_explainer_packet()
    write_continuity_degradation_explainer_packet(OUT_PATH, packet)
    logging.getLogger("continuity_degradation_explainer").info(
        "continuity_degradation_explainer_completed final_status=%s explanation_posture=%s",
        packet["final_status"],
        packet["explanation_posture"],
    )
    print(f"{packet['final_status']} {packet['explanation_posture']}")


if __name__ == "__main__":
    main()
