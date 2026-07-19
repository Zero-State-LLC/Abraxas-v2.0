from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.sync.v2_live_notion_surface_reconciliation import (  # noqa: E402
    build_v2_live_notion_surface_reconciliation,
    write_v2_live_notion_surface_reconciliation,
    write_v2_live_notion_surface_reconciliation_markdown,
)

OUT_JSON = Path("out/sync/v2_live_notion_surface_reconciliation/latest.json")
OUT_MD = Path("out/sync/v2_live_notion_surface_reconciliation/latest.md")


def run(
    *,
    repo_root: str | Path = ".",
    out_json: str | Path = OUT_JSON,
    out_md: str | Path = OUT_MD,
) -> dict:
    root = Path(repo_root)
    packet = build_v2_live_notion_surface_reconciliation(root)
    json_target = root / out_json
    md_target = root / out_md
    write_v2_live_notion_surface_reconciliation(json_target, packet)
    write_v2_live_notion_surface_reconciliation_markdown(md_target, packet)
    return packet


if __name__ == "__main__":
    result = run()
    print(result["reconciliation_status"])
    print(result["recommended_next_lane"])
