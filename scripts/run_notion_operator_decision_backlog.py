from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.sync.notion_operator_decision_backlog import (  # noqa: E402
    OUT_JSON,
    OUT_MD,
    build_notion_operator_decision_backlog,
    write_notion_operator_decision_backlog,
    write_notion_operator_decision_backlog_markdown,
)
from core.sync.notion_spec_completion_queue import OUT_JSON as COMPLETION_QUEUE_JSON  # noqa: E402


def run(
    *,
    repo_root: str | Path = ROOT,
    out_json: str | Path | None = None,
    out_md: str | Path | None = None,
    completion_queue_path: str | Path = COMPLETION_QUEUE_JSON,
) -> dict:
    root = Path(repo_root)
    packet = build_notion_operator_decision_backlog(
        repo_root=root,
        completion_queue_path=completion_queue_path,
    )
    json_target = root / (Path(out_json) if out_json is not None else Path(OUT_JSON))
    md_target = root / (Path(out_md) if out_md is not None else Path(OUT_MD))
    write_notion_operator_decision_backlog(json_target, packet)
    write_notion_operator_decision_backlog_markdown(md_target, packet)
    return packet


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--completion-queue", default=COMPLETION_QUEUE_JSON)
    args = parser.parse_args()
    packet = run(completion_queue_path=args.completion_queue)
    print(packet["backlog_id"])
    print(packet["backlog_status"])
    print(packet["top_priority_surface"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
