from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.config import RuntimePaths  # noqa: E402
from core.operator_narrative_static_archive_package_language_boundary_audit import (  # noqa: E402
    build_operator_narrative_static_archive_package_language_boundary_audit_packet,
    write_operator_narrative_static_archive_package_language_boundary_audit,
)


def main() -> int:
    paths = RuntimePaths.from_env()
    out = paths.audit_dir / "operator_narrative_static_archive_package_language_boundary_audit_001.latest.json"
    packet = build_operator_narrative_static_archive_package_language_boundary_audit_packet(repo_root=ROOT)
    write_operator_narrative_static_archive_package_language_boundary_audit(out, packet)
    print(packet["final_status"])
    print(packet["audit_posture"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
