from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.ingest.auto_ingest_validation_pack import (  # noqa: E402
    build_auto_ingest_validation_pack,
    write_auto_ingest_validation_pack,
)

OUT = Path("out/audit/abx_auto_ingest_validation_pack_001.latest.json")


def main() -> None:
    packet = build_auto_ingest_validation_pack()
    write_auto_ingest_validation_pack(OUT, packet)
    print(packet["final_status"])
    print(packet["validation_hash"])


if __name__ == "__main__":
    main()
