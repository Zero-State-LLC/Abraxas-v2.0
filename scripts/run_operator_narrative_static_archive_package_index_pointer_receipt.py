from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.config import RuntimePaths  # noqa: E402
from core.operator_narrative_static_archive_package_index_pointer_receipt import (  # noqa: E402
    build_operator_narrative_static_archive_package_index_pointer_receipt_packet,
    write_operator_narrative_static_archive_package_index_pointer_receipt,
)


def main() -> int:
    paths = RuntimePaths.from_env()
    out = paths.audit_dir / "operator_narrative_static_archive_package_index_pointer_receipt_001.latest.json"
    pkt = build_operator_narrative_static_archive_package_index_pointer_receipt_packet(repo_root=ROOT)
    write_operator_narrative_static_archive_package_index_pointer_receipt(out, pkt)
    print(pkt.get("final_status", ""))
    print(pkt.get("index_posture", ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
