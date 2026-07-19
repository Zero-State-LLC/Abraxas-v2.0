from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.repo_notion_diff import OUT_JSON as REPO_NOTION_DIFF_JSON  # noqa: E402
from core.sync.notion_patch_queue_terminal_state import OUT_JSON as TERMINAL_STATE_JSON  # noqa: E402
from core.sync.global_ingest_adapter_spine_alignment_plan import (  # noqa: E402
    OUT_JSON,
    OUT_MD,
    build_global_ingest_adapter_spine_alignment_plan,
    write_global_ingest_adapter_spine_alignment_plan,
    write_global_ingest_adapter_spine_alignment_plan_markdown,
)


def run(
    *,
    repo_root: str | Path = ROOT,
    out_json: str | Path | None = None,
    out_md: str | Path | None = None,
    terminal_state_path: str | Path = TERMINAL_STATE_JSON,
    repo_notion_diff_path: str | Path = REPO_NOTION_DIFF_JSON,
) -> dict:
    root = Path(repo_root)
    packet = build_global_ingest_adapter_spine_alignment_plan(
        repo_root=root,
        terminal_state_path=terminal_state_path,
        repo_notion_diff_path=repo_notion_diff_path,
    )
    json_target = root / (Path(out_json) if out_json is not None else Path(OUT_JSON))
    md_target = root / (Path(out_md) if out_md is not None else Path(OUT_MD))
    write_global_ingest_adapter_spine_alignment_plan(json_target, packet)
    write_global_ingest_adapter_spine_alignment_plan_markdown(md_target, packet)
    return packet


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--terminal-state", default=TERMINAL_STATE_JSON)
    parser.add_argument("--repo-notion-diff", default=REPO_NOTION_DIFF_JSON)
    args = parser.parse_args()
    packet = run(
        terminal_state_path=args.terminal_state,
        repo_notion_diff_path=args.repo_notion_diff,
    )
    print(packet["plan_id"])
    print(packet["plan_status"])
    print(packet["recommended_next_patch"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
