from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.priority2_live_console_migration_closeout import (  # noqa: E402
    DEFAULT_OUT_PATH,
    build_priority2_live_console_migration_closeout_receipt,
    write_priority2_live_console_migration_closeout_receipt,
)


def run(*, repo_root: Path | None = None, out_path: Path | None = None) -> dict[str, object]:
    root = repo_root or ROOT
    target = out_path or (root / DEFAULT_OUT_PATH)
    packet = build_priority2_live_console_migration_closeout_receipt(repo_root=root)
    target.parent.mkdir(parents=True, exist_ok=True)
    write_priority2_live_console_migration_closeout_receipt(target, packet)
    return packet


def main() -> int:
    packet = run()
    print(f"status: {packet['status']}")
    print(f"canonical_hash: {packet['canonical_hash']}")
    print(f"receipt_path: {DEFAULT_OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
