from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.global_pipeline_gap_backlog import write_global_pipeline_gap_backlog  # noqa: E402


def main() -> int:
    packet = write_global_pipeline_gap_backlog()
    print(packet["status"])
    print(packet["backlog_id"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
