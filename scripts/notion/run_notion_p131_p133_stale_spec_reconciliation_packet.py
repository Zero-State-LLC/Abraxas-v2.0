from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.notion_p131_p133_stale_spec_reconciliation_packet import (  # noqa: E402
    OUT_PATH,
    write_notion_p131_p133_stale_spec_reconciliation_packet,
)


def main() -> int:
    packet = write_notion_p131_p133_stale_spec_reconciliation_packet(ROOT)
    print(packet["packet_id"])
    print(packet["status"])
    print(OUT_PATH)
    return 0 if packet["status"].endswith("_READY") else 1


if __name__ == "__main__":
    raise SystemExit(main())
