from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import RuntimePaths
from core.operator_narrative_archive_chain_closure_receipt import (
    build_operator_narrative_archive_chain_closure_receipt_packet,
    write_operator_narrative_archive_chain_closure_receipt,
)

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.operator_narrative_archive_chain_closure_receipt_latest


def main() -> int:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    packet = build_operator_narrative_archive_chain_closure_receipt_packet()
    write_operator_narrative_archive_chain_closure_receipt(OUT_PATH, packet)
    print(f"final_status={packet['final_status']}")
    print(f"closure_posture={packet['closure_posture']}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
