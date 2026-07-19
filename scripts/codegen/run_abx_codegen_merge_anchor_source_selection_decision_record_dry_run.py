from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.abx_codegen_merge_anchor_source_selection_decision_record_dry_run import (  # noqa: E402
    write_abx_codegen_merge_anchor_source_selection_decision_record_dry_run,
)

OUT_JSON = Path("out/operator_review/abx_codegen_merge_anchor_source_selection_decision_record_dry_run_001.latest.json")  # noqa: E501
OUT_MD = OUT_JSON.with_suffix(".md")


def run(*, repo_root: str | Path = ROOT, out_root: str | Path | None = None) -> dict[str, object]:
    return write_abx_codegen_merge_anchor_source_selection_decision_record_dry_run(
        repo_root,
        out_root=out_root,
    )


def main() -> int:
    packet = run()
    print(packet["status"])
    print(packet["recommended_next_patch"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
