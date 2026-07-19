from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.repo_notion_diff import (  # noqa: E402
    OUT_JSON,
    OUT_MD,
    build_repo_notion_diff,
    write_repo_notion_diff,
    write_repo_notion_diff_markdown,
)


def run(
    *,
    repo_root: str | Path = ROOT,
    out_json: str | Path | None = None,
    out_md: str | Path | None = None,
) -> dict:
    root = Path(repo_root)
    packet = build_repo_notion_diff(repo_root=root)
    json_target = root / (Path(out_json) if out_json is not None else Path(OUT_JSON))
    md_target = root / (Path(out_md) if out_md is not None else Path(OUT_MD))
    write_repo_notion_diff(json_target, packet)
    write_repo_notion_diff_markdown(md_target, packet)
    return packet


def main() -> int:
    packet = run()
    print(packet["diff_id"])
    print(packet["diff_status"])
    print(packet["recommended_next_patch"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
