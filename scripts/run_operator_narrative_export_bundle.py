from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import RuntimePaths
from core.operator_narrative_export_bundle import (
    build_operator_narrative_export_bundle_packet,
    write_operator_narrative_export_bundle_packet,
)


def main() -> int:
    paths = RuntimePaths.from_env()
    out = paths.operator_narrative_export_bundle_latest
    out.parent.mkdir(parents=True, exist_ok=True)
    packet = build_operator_narrative_export_bundle_packet()
    write_operator_narrative_export_bundle_packet(out, packet)
    logging.getLogger("operator_narrative_export_bundle").info(
        "operator_narrative_export_bundle_completed final_status=%s export_posture=%s",
        packet["final_status"],
        packet["export_posture"],
    )
    print(f"final_status={packet['final_status']} export_posture={packet['export_posture']}")
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    raise SystemExit(main())
