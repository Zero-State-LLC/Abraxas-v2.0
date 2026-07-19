"""Script: emit deterministic P29 operator attention weather artifacts."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.config import RuntimePaths
from core.operator_attention_weather import (
    build_operator_attention_weather_packet,
    write_operator_attention_weather_packet,
)

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.operator_attention_weather_latest


def main() -> None:
    packet = build_operator_attention_weather_packet()
    write_operator_attention_weather_packet(OUT_PATH, packet)
    logging.info(
        "operator_attention_weather_completed final_status=%s weather_posture=%s",
        packet["final_status"],
        packet["weather_posture"],
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
