"""Script: emit deterministic P31 operator attention ledger artifacts."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import RuntimePaths
from core.operator_attention_ledger import (
    build_operator_attention_ledger_packet,
    write_operator_attention_ledger_packet,
)

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.operator_attention_ledger_latest


def main() -> None:
    packet = build_operator_attention_ledger_packet()
    write_operator_attention_ledger_packet(OUT_PATH, packet)
    logging.info(
        "operator_attention_ledger_completed final_status=%s ledger_posture=%s",
        packet["final_status"],
        packet["ledger_posture"],
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
