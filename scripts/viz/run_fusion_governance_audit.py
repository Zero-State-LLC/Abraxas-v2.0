from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.config import RuntimePaths
from core.fusion_governance_audit import build_fusion_governance_audit_receipt, write_fusion_governance_audit_receipt

_PATHS = RuntimePaths.from_env()
OUT = _PATHS.audit_dir / "fusion_governance_audit_001.latest.json"


def main() -> int:
    packet = build_fusion_governance_audit_receipt()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    write_fusion_governance_audit_receipt(Path(OUT), packet)
    print(f"[fusion-governance-audit] final_status={packet['final_status']} audit_posture={packet['audit_posture']}")
    print(f"[fusion-governance-audit] wrote: {OUT.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
