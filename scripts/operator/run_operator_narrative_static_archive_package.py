from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.config import RuntimePaths  # noqa: E402
from core.operator_narrative_static_archive_package import (  # noqa: E402
    build_operator_narrative_static_archive_package_packet,
    write_operator_narrative_static_archive_package,
)


def main() -> int:
    paths = RuntimePaths.from_env()
    out = paths.out_dir / "package" / "operator_narrative_static_archive_package_001.latest.json"
    packet = build_operator_narrative_static_archive_package_packet(repo_root=ROOT)
    write_operator_narrative_static_archive_package(out, packet)
    print(packet["final_status"])
    print(packet["package_posture"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
