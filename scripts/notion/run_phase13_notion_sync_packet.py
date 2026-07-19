from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.preflight_notion_phase13_sync_packet import (  # noqa: E402
    write_phase13_notion_sync_packet,
)

OUT_JSON_PATH = Path("out/sync/phase13_notion_sync_packet_001.latest.json")


def run(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    return write_phase13_notion_sync_packet(repo_root, out_root=out_root)


def main() -> None:
    packet = run()
    print(f"wrote {OUT_JSON_PATH}")
    print(f"status={packet['status']}")
    print(f"sync_packet_hash={packet['sync_packet_hash']}")


if __name__ == "__main__":
    main()
