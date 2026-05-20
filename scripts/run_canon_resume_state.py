from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.canon_resume_state import build_canon_resume_state, write_canon_resume_state  # noqa: E402


def run(
    *,
    repo_root: str | Path = ROOT,
    out_path: str | Path = ROOT / "out/canon_resume_state/latest.json",
) -> dict[str, object]:
    packet = build_canon_resume_state(repo_root=repo_root)
    write_canon_resume_state(Path(out_path), packet)
    return packet


def main() -> int:
    packet = run()
    print(packet["recommended_resume_lane"])
    print(packet["canonical_status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
