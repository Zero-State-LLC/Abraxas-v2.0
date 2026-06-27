from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.codegen.oracle_signal.oracle_runtime_execution_notion_mirror import (  # noqa: E402
    write_oracle_full_live_runtime_execution_attempt_notion_mirror_packet,
)


def main() -> int:
    packet = write_oracle_full_live_runtime_execution_attempt_notion_mirror_packet(
        ROOT
    )
    print(
        "out/sync/"
        "oracle_full_live_runtime_execution_attempt_notion_mirror_packet_001.latest.json"
    )
    print(packet["canonical_hash"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
