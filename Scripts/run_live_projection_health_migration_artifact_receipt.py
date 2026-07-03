from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.live_projection_health_migration_artifact import (  # noqa: E402
    DEFAULT_OUT_PATH,
    build_live_projection_health_migration_artifact_receipt,
    write_live_projection_health_migration_artifact_receipt,
)


def run(*, repo_root: Path = REPO_ROOT, out_path: Path | None = None) -> dict:
    target = out_path or repo_root / DEFAULT_OUT_PATH
    packet = build_live_projection_health_migration_artifact_receipt(repo_root=repo_root)
    target.parent.mkdir(parents=True, exist_ok=True)
    write_live_projection_health_migration_artifact_receipt(target, packet)
    return packet


def main() -> int:
    packet = run()
    print(f"status: {packet['status']}")
    print(f"canonical_hash: {packet['canonical_hash']}")
    print(f"receipt_path: {DEFAULT_OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
