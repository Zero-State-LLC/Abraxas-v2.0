from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.config import RuntimePaths
from core.operator_narrative_report_governance_audit import (
    build_operator_narrative_report_governance_audit,
    write_operator_narrative_report_governance_audit,
)

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.operator_narrative_report_governance_audit_latest


def main() -> int:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    packet = build_operator_narrative_report_governance_audit()
    write_operator_narrative_report_governance_audit(OUT_PATH, packet)
    logging.getLogger("operator_narrative_report_governance_audit").info(
        "operator_narrative_report_governance_audit_completed final_status=%s audit_posture=%s",
        packet["final_status"],
        packet["audit_posture"],
    )
    print(f"final_status={packet['final_status']} audit_posture={packet['audit_posture']}")
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    raise SystemExit(main())
