from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.abx_codegen_intelligence_spine_shadow_binding import (  # noqa: E402
    BINDING_JSON_PATH,
    write_abx_codegen_intelligence_spine_shadow_binding_packet,
)
from core.abx_codegen_intelligence_spine_shadow_replay_harness import (  # noqa: E402
    write_abx_codegen_intelligence_spine_shadow_replay_harness_packet,
)


def main() -> int:
    write_abx_codegen_intelligence_spine_shadow_replay_harness_packet(ROOT)
    packet = write_abx_codegen_intelligence_spine_shadow_binding_packet(ROOT)
    print(packet["binding_id"])
    print(packet["status"])
    print(BINDING_JSON_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
