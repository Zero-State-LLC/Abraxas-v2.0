from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.sync.v2_hygiene_phase1_clean_frontier_operator_authorization_bridge import (  # noqa: E402
    write_v2_hygiene_phase1_clean_frontier_operator_authorization_bridge,
)
from core.sync.v2_hygiene_phase1_duplicate_frontier_quarantine_repair_execution_receipt import (  # noqa: E402
    RECEIPT_JSON_PATH,
    write_v2_hygiene_phase1_duplicate_frontier_quarantine_repair_execution_receipt,
)

OUT_JSON_PATH = Path("out/operator_review/v2_hygiene_phase1_duplicate_frontier_quarantine_repair_execution_receipt_001.latest.json")
OUT_MD_PATH = OUT_JSON_PATH.with_suffix(".md")


def run(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
    source_design_receipt_path: str | Path = (
        "out/operator_review/"
        "v2_hygiene_phase1_duplicate_frontier_quarantine_design_receipt_001.latest.json"
    ),
    execute_repair: bool = True,
) -> dict[str, Any]:
    write_v2_hygiene_phase1_clean_frontier_operator_authorization_bridge(
        repo_root,
        out_root=out_root,
    )
    return write_v2_hygiene_phase1_duplicate_frontier_quarantine_repair_execution_receipt(
        repo_root,
        out_root=out_root,
        source_design_receipt_path=source_design_receipt_path,
        execute_repair=execute_repair,
    )


def main() -> None:
    packet = run(execute_repair=True)
    print(f"wrote {RECEIPT_JSON_PATH}")
    print(f"status={packet['status']}")
    print(f"repair_execution_receipt_hash={packet['repair_execution_receipt_hash']}")


if __name__ == "__main__":
    main()
