from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from core.continuity_namespace_audit import (  # noqa: E402
    build_continuity_namespace_audit,
    write_continuity_namespace_audit,
)

OUT_PATH = Path("out/continuity_namespace_audit/latest.json")


def run(repo_root: Path | str | None = None, output_path: Path | str | None = None) -> dict:
    root = Path(repo_root) if repo_root is not None else Path(__file__).resolve().parent.parent.parent
    target = root / (Path(output_path) if output_path is not None else OUT_PATH)
    packet = build_continuity_namespace_audit(repo_root=root)
    write_continuity_namespace_audit(target, packet)
    return packet


def main() -> None:
    packet = run()
    print(packet["audit_id"])
    print(packet["recommended_next_lane"])


if __name__ == "__main__":
    main()
