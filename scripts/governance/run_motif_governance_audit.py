from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.config import RuntimePaths
from core.motif_governance_audit import build_motif_governance_audit_receipt, write_motif_governance_audit_receipt


def main() -> int:
    paths = RuntimePaths.from_env()
    out = paths.audit_dir / "motif_governance_audit_001.latest.json"
    packet = build_motif_governance_audit_receipt()
    out.parent.mkdir(parents=True, exist_ok=True)
    write_motif_governance_audit_receipt(out, packet)
    print(f"status={packet['final_status']} posture={packet['audit_posture']} path={out.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
