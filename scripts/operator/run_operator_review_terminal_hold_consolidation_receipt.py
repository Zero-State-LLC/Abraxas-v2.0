from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.sync.operator_review_terminal_hold_consolidation_receipt import (  # noqa: E402
    build_operator_review_terminal_hold_consolidation_receipt,
    write_operator_review_terminal_hold_consolidation_receipt,
    write_operator_review_terminal_hold_consolidation_receipt_markdown,
)

OUT_JSON = Path("out/operator_review/operator_review_terminal_hold_consolidation_receipt_001.latest.json")
OUT_MD = Path("out/operator_review/operator_review_terminal_hold_consolidation_receipt_001.latest.md")


def run(
    *,
    repo_root: str | Path = ".",
    out_json: str | Path = OUT_JSON,
    out_md: str | Path = OUT_MD,
) -> dict:
    packet = build_operator_review_terminal_hold_consolidation_receipt(repo_root)
    json_target = Path(repo_root) / out_json
    md_target = Path(repo_root) / out_md
    write_operator_review_terminal_hold_consolidation_receipt(json_target, packet)
    write_operator_review_terminal_hold_consolidation_receipt_markdown(md_target, packet)
    return packet


if __name__ == "__main__":
    result = run()
    print(result["receipt_status"])
    print(result["recommended_next_lane"])
