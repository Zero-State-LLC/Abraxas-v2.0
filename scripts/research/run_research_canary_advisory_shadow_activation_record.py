from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.research_canary_advisory_shadow_activation_record import (  # noqa: E402
    write_research_canary_advisory_shadow_activation_record,
)


def main() -> int:
    packet = write_research_canary_advisory_shadow_activation_record(ROOT)
    print(packet["lane_id"])
    print(packet["status"])
    print(packet["recommended_next_lane"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
