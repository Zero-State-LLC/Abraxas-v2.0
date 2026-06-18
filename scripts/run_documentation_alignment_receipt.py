from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.sync.documentation_alignment_receipt import write_documentation_alignment_receipt  # noqa: E402


def run(*, repo_root: str | Path = ROOT, out_root: str | Path | None = None) -> dict[str, object]:
    return write_documentation_alignment_receipt(repo_root=repo_root, out_root=out_root)


def main() -> int:
    packet = run()
    print(packet["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
