from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.ingest.controlled_ingest_scheduler_governance_audit import (  # noqa: E402
    build_controlled_ingest_scheduler_governance_audit_packet,
    write_controlled_ingest_scheduler_governance_audit,
)

OUT = Path("out/audit/controlled_ingest_scheduler_governance_audit_001.latest.json")


def main() -> int:
    packet = build_controlled_ingest_scheduler_governance_audit_packet()
    write_controlled_ingest_scheduler_governance_audit(OUT, packet)
    print(f"[controlled-ingest-governance-audit] final_status={packet['final_status']} audit_posture={packet['audit_posture']}")
    print(f"[controlled-ingest-governance-audit] wrote: {OUT.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
