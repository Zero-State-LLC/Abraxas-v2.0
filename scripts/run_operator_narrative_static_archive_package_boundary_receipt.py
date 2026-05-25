#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def main() -> int:
    from core.config import RuntimePaths
    from core.operator_narrative_static_archive_package_boundary_receipt import (
        build_operator_narrative_static_archive_package_boundary_receipt_packet,
        write_operator_narrative_static_archive_package_boundary_receipt,
    )

    paths = RuntimePaths.from_env()
    out = paths.audit_dir / "operator_narrative_static_archive_package_boundary_receipt_001.latest.json"
    packet = build_operator_narrative_static_archive_package_boundary_receipt_packet(
        p58_planning_path="docs/plans/P58_planning_gate_static_archive_package.md",
        p57_receipt_path=paths.operator_narrative_archive_chain_global_verification_latest,
        repo_root=Path("."),
    )
    write_operator_narrative_static_archive_package_boundary_receipt(out, packet)
    print(packet["final_status"])
    print(packet["boundary_posture"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
