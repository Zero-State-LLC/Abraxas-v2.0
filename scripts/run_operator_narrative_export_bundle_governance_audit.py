from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from core.config import RuntimePaths
from core.operator_narrative_export_bundle_governance_audit import (
    build_operator_narrative_export_bundle_governance_audit_packet,
    write_operator_narrative_export_bundle_governance_audit,
)


def main() -> int:
    paths = RuntimePaths.from_env()
    out = paths.operator_narrative_export_bundle_governance_audit_latest
    packet = build_operator_narrative_export_bundle_governance_audit_packet(
        export_bundle_path=paths.operator_narrative_export_bundle_latest,
        export_bundle_markdown_path=paths.operator_narrative_export_bundle_latest.with_suffix(".md"),
    )
    write_operator_narrative_export_bundle_governance_audit(out, packet)
    logging.getLogger("operator_narrative_export_bundle_governance_audit").info(
        "operator_narrative_export_bundle_governance_audit_completed final_status=%s audit_posture=%s",
        packet.get("final_status", ""),
        packet.get("audit_posture", ""),
    )
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    raise SystemExit(main())
