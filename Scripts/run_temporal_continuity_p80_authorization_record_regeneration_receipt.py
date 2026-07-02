from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.temporal_continuity_p80_authorization_record_regeneration_receipt import (  # noqa: E402,E501
    DEFAULT_OUT_PATH,
    build_temporal_continuity_p80_authorization_record_regeneration_receipt,
    write_temporal_continuity_p80_authorization_record_regeneration_receipt,
)


def run(
    *,
    repo_root: str | Path = ROOT,
    out_path: str | Path | None = None,
) -> dict[str, object]:
    packet = build_temporal_continuity_p80_authorization_record_regeneration_receipt(
        repo_root=repo_root
    )
    target = (
        Path(out_path)
        if out_path is not None
        else Path(repo_root) / DEFAULT_OUT_PATH
    )
    write_temporal_continuity_p80_authorization_record_regeneration_receipt(
        target,
        packet,
    )
    return packet


def main() -> int:
    packet = run()
    print(f"status: {packet['status']}")
    print(f"canonical_hash: {packet['canonical_hash']}")
    print(
        "p80_regeneration_plan_status: "
        f"{packet['p80_regeneration_summary']['p80_regeneration_plan_status']}"
    )
    print(f"receipt_path: {DEFAULT_OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
