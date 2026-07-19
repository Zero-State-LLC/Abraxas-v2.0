from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.sync.notion_writeback_authorization_gate import (  # noqa: E402
    DEFAULT_OPERATOR_AUTHORIZATION_PATH,
    DRY_RUN_PLAN_PATH,
    OUT_JSON,
    OUT_MD,
    build_notion_writeback_authorization_gate,
    write_notion_writeback_authorization_gate,
    write_notion_writeback_authorization_gate_markdown,
)


def run(
    *,
    repo_root: str | Path = ROOT,
    out_json: str | Path | None = None,
    out_md: str | Path | None = None,
    dry_run_plan_path: str = DRY_RUN_PLAN_PATH,
    operator_authorization_path: str = DEFAULT_OPERATOR_AUTHORIZATION_PATH,
) -> dict:
    root = Path(repo_root)
    packet = build_notion_writeback_authorization_gate(
        repo_root=root,
        dry_run_plan_path=dry_run_plan_path,
        operator_authorization_path=operator_authorization_path,
    )
    json_target = root / (Path(out_json) if out_json is not None else Path(OUT_JSON))
    md_target = root / (Path(out_md) if out_md is not None else Path(OUT_MD))
    write_notion_writeback_authorization_gate(json_target, packet)
    write_notion_writeback_authorization_gate_markdown(md_target, packet)
    return packet


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run-plan", default=DRY_RUN_PLAN_PATH)
    parser.add_argument("--operator-authorization", default=DEFAULT_OPERATOR_AUTHORIZATION_PATH)
    args = parser.parse_args()
    packet = run(
        dry_run_plan_path=args.dry_run_plan,
        operator_authorization_path=args.operator_authorization,
    )
    print(packet["gate_id"])
    print(packet["gate_status"])
    print(packet["recommended_next_lane"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
