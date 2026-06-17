from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.notion_repo_sync_audit_writeback_receipt import (  # noqa: E402
    build_notion_repo_sync_audit_writeback_receipt,
    write_notion_repo_sync_audit_writeback_receipt,
    write_notion_repo_sync_audit_writeback_receipt_markdown,
)

OUT_JSON = Path("out/audit/notion_repo_sync_audit_writeback_receipt_001.latest.json")
OUT_MD = OUT_JSON.with_suffix(".md")


def run(
    *,
    repo_root: str | Path = ROOT,
    out_json: str | Path | None = None,
    out_md: str | Path | None = None,
) -> dict:
    root = Path(repo_root)
    packet = build_notion_repo_sync_audit_writeback_receipt(repo_root=root)
    json_target = root / (Path(out_json) if out_json is not None else OUT_JSON)
    md_target = root / (Path(out_md) if out_md is not None else OUT_MD)
    write_notion_repo_sync_audit_writeback_receipt(json_target, packet)
    write_notion_repo_sync_audit_writeback_receipt_markdown(md_target, packet)
    return packet


def main() -> int:
    packet = run()
    print(packet["receipt_id"])
    print(packet["receipt_status"])
    print(packet["recommended_next_lane"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
