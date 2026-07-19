from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.runtime_integration_gate_shadow_wiring_plan import (  # noqa: E402
    write_runtime_integration_gate_shadow_wiring_plan,
)


def main() -> int:
    packet = write_runtime_integration_gate_shadow_wiring_plan(ROOT)
    print(packet["plan_id"])
    print(packet["status"])
    print(packet["recommended_next_lane"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
