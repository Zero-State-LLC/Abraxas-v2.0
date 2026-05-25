from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import RuntimePaths
from core.operator_narrative_report import (
    build_operator_narrative_report_packet,
    write_operator_narrative_report_packet,
)

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.operator_narrative_report_latest


def main() -> int:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    packet = build_operator_narrative_report_packet()
    write_operator_narrative_report_packet(OUT_PATH, packet)
    logging.getLogger("operator_narrative_report").info(
        "operator_narrative_report_completed final_status=%s report_posture=%s",
        packet["final_status"],
        packet["report_posture"],
    )
    print(f"final_status={packet['final_status']} report_posture={packet['report_posture']}")
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    raise SystemExit(main())
