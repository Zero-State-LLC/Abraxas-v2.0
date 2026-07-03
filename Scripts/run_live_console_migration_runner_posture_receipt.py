from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.live_console_migration_runner_posture import (  # noqa: E402
    DEFAULT_OUT_PATH,
    build_live_console_migration_runner_posture_receipt,
    write_live_console_migration_runner_posture_receipt,
)


def run(
    *,
    repo_root: str | Path = ROOT,
    out_path: str | Path | None = None,
) -> dict[str, object]:
    packet = build_live_console_migration_runner_posture_receipt(repo_root=repo_root)
    target = Path(out_path) if out_path is not None else Path(repo_root) / DEFAULT_OUT_PATH
    write_live_console_migration_runner_posture_receipt(target, packet)
    return packet


def main() -> int:
    packet = run()
    print(f"status: {packet['status']}")
    print(f"canonical_hash: {packet['canonical_hash']}")
    print(f"receipt_path: {DEFAULT_OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
