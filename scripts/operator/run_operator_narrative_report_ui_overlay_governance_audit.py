from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.config import RuntimePaths
from core.operator_narrative_report_ui_overlay_governance_audit import (
    build_operator_narrative_report_ui_overlay_governance_audit,
    write_operator_narrative_report_ui_overlay_governance_audit,
)


def main() -> int:
    paths = RuntimePaths.from_env()
    packet = build_operator_narrative_report_ui_overlay_governance_audit()
    out = paths.operator_narrative_report_ui_overlay_governance_audit_latest
    out.parent.mkdir(parents=True, exist_ok=True)
    write_operator_narrative_report_ui_overlay_governance_audit(out, packet)
    print(f"final_status={packet['final_status']} audit_posture={packet['audit_posture']}")
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    raise SystemExit(main())
