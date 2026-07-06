from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.hyperstition_evaluator_deepening import (  # noqa: E402
    DEFAULT_OUT_PATH,
    build_hyperstition_evaluator_deepening_receipt,
    write_hyperstition_evaluator_deepening_receipt,
)


def run(
    *,
    repo_root: str | Path = ROOT,
    out_path: str | Path | None = None,
) -> dict[str, object]:
    packet = build_hyperstition_evaluator_deepening_receipt(repo_root=repo_root)
    target = (
        Path(out_path)
        if out_path is not None
        else Path(repo_root) / DEFAULT_OUT_PATH
    )
    write_hyperstition_evaluator_deepening_receipt(target, packet)
    return json.loads(target.read_text(encoding="utf-8"))


def main() -> int:
    packet = run()
    print(f"status: {packet['status']}")
    print(f"canonical_hash: {packet['canonical_hash']}")
    print(f"receipt_path: {DEFAULT_OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
