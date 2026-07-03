from __future__ import annotations

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.temporal_upstream_status_plan_regeneration_execution_route_refresh import (  # noqa: E402
    DEFAULT_OUT_PATH,
    build_temporal_upstream_status_plan_regeneration_execution_route_refresh_receipt,
    write_temporal_upstream_status_plan_regeneration_execution_route_refresh_receipt,
)


def run(*, repo_root: Path | None = None, out_path: Path | None = None):
    root = repo_root or REPO_ROOT
    target = out_path or (root / DEFAULT_OUT_PATH)
    packet = (
        build_temporal_upstream_status_plan_regeneration_execution_route_refresh_receipt(
            repo_root=root
        )
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    write_temporal_upstream_status_plan_regeneration_execution_route_refresh_receipt(
        target, packet
    )
    return packet


def main() -> int:
    packet = run()
    print(f"status: {packet['status']}")
    print(f"canonical_hash: {packet['canonical_hash']}")
    print(f"receipt_path: {DEFAULT_OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
