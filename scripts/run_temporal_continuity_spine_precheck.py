from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.temporal_continuity_spine_precheck import (  # noqa: E402
    build_temporal_continuity_spine_precheck,
    write_temporal_continuity_spine_precheck,
)

OUT_PATH = Path("out/temporal_continuity_spine_precheck/latest.json")


def run(
    *,
    repo_root: str | Path = ROOT,
    out_path: str | Path | None = None,
) -> dict[str, object]:
    packet = build_temporal_continuity_spine_precheck(repo_root=repo_root)
    target = Path(out_path) if out_path is not None else Path(repo_root) / OUT_PATH
    write_temporal_continuity_spine_precheck(target, packet)
    return packet


def main() -> int:
    packet = run()
    print(packet["recommended_next_lane"])
    print(packet["canonical_status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
