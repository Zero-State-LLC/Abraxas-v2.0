from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.config import RuntimePaths  # noqa: E402
from core.operator_narrative_static_archive_package_final_index_receipt import (  # noqa: E402
    build_operator_narrative_static_archive_package_final_index_receipt_packet,
    write_operator_narrative_static_archive_package_final_index_receipt,
)


def main() -> int:
    paths = RuntimePaths.from_env()
    out_path = paths.operator_narrative_static_archive_package_final_index_receipt_latest
    out_path.parent.mkdir(parents=True, exist_ok=True)
    packet = build_operator_narrative_static_archive_package_final_index_receipt_packet(repo_root=ROOT)
    write_operator_narrative_static_archive_package_final_index_receipt(out_path, packet)
    print(packet["final_status"])
    print(packet["final_index_posture"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
