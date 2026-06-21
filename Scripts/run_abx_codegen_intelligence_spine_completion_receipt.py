from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.codegen.spine_completion import (  # noqa: E402
    OUT_JSON,
    OUT_MD,
    write_codegen_spine_completion_receipt,
)


def run(
    *,
    repo_root: str | Path = ROOT,
    out_json: str | Path = OUT_JSON,
    out_md: str | Path = OUT_MD,
) -> dict:
    return write_codegen_spine_completion_receipt(
        repo_root=repo_root,
        out_json=out_json,
        out_md=out_md,
    )


def main() -> int:
    receipt = run()
    print(receipt["receipt_id"])
    print(receipt["spine_status"])
    print(receipt["canonical_hash"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
