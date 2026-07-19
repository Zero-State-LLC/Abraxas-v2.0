from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.sync.notion_writeback_dry_run_plan import (  # noqa: E402
    DEFAULT_SOURCE_ARTIFACTS,
    OUT_JSON,
    OUT_MD,
    build_notion_writeback_dry_run_plan,
    write_notion_writeback_dry_run_plan,
    write_notion_writeback_dry_run_plan_markdown,
)


def run(
    *,
    repo_root: str | Path = ROOT,
    out_json: str | Path | None = None,
    out_md: str | Path | None = None,
    target_page_id: str = "NOT_COMPUTABLE",
    target_label: str = "NOT_COMPUTABLE",
    source_artifacts: tuple[str, ...] = DEFAULT_SOURCE_ARTIFACTS,
) -> dict:
    root = Path(repo_root)
    packet = build_notion_writeback_dry_run_plan(
        repo_root=root,
        target_page_id=target_page_id,
        target_label=target_label,
        source_artifacts=source_artifacts,
    )
    json_target = root / (Path(out_json) if out_json is not None else Path(OUT_JSON))
    md_target = root / (Path(out_md) if out_md is not None else Path(OUT_MD))
    write_notion_writeback_dry_run_plan(json_target, packet)
    write_notion_writeback_dry_run_plan_markdown(md_target, packet)
    return packet


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-page-id", default="NOT_COMPUTABLE")
    parser.add_argument("--target-label", default="NOT_COMPUTABLE")
    parser.add_argument("--artifact", action="append", default=[])
    args = parser.parse_args()
    source_artifacts = tuple(args.artifact) if args.artifact else DEFAULT_SOURCE_ARTIFACTS
    packet = run(
        target_page_id=args.target_page_id,
        target_label=args.target_label,
        source_artifacts=source_artifacts,
    )
    print(packet["plan_id"])
    print(packet["plan_status"])
    print(packet["recommended_next_lane"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
