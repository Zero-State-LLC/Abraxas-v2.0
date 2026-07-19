#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def main() -> int:
    from core.config import RuntimePaths
    from core.operator_narrative_static_archive_package_preflight_receipt import (
        build_operator_narrative_static_archive_package_preflight_receipt_packet,
        write_operator_narrative_static_archive_package_preflight_receipt,
    )

    paths = RuntimePaths.from_env()
    out = paths.audit_dir / "operator_narrative_static_archive_package_preflight_receipt_001.latest.json"
    packet = build_operator_narrative_static_archive_package_preflight_receipt_packet(
        p60_planning_path="docs/plans/P60_planning_gate_static_archive_package_implementation.md",
        p59_receipt_path=paths.operator_narrative_static_archive_package_boundary_receipt_latest,
        repo_root=Path("."),
    )
    write_operator_narrative_static_archive_package_preflight_receipt(out, packet)
    print(packet["final_status"])
    print(packet["preflight_posture"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
