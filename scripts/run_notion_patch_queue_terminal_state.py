from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.rune_registry_formalization_plan import OUT_JSON as RUNE_REGISTRY_FORMALIZATION_PLAN_JSON  # noqa: E402
from core.sync.notion_patch_queue_terminal_state import (  # noqa: E402
    OUT_JSON,
    OUT_MD,
    build_notion_patch_queue_terminal_state,
    write_notion_patch_queue_terminal_state,
    write_notion_patch_queue_terminal_state_markdown,
)


def run(
    *,
    repo_root: str | Path = ROOT,
    out_json: str | Path | None = None,
    out_md: str | Path | None = None,
    rune_registry_formalization_plan_path: str | Path = RUNE_REGISTRY_FORMALIZATION_PLAN_JSON,
) -> dict:
    root = Path(repo_root)
    packet = build_notion_patch_queue_terminal_state(
        repo_root=root,
        rune_registry_formalization_plan_path=rune_registry_formalization_plan_path,
    )
    json_target = root / (Path(out_json) if out_json is not None else Path(OUT_JSON))
    md_target = root / (Path(out_md) if out_md is not None else Path(OUT_MD))
    write_notion_patch_queue_terminal_state(json_target, packet)
    write_notion_patch_queue_terminal_state_markdown(md_target, packet)
    return packet


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--rune-registry-formalization-plan",
        default=RUNE_REGISTRY_FORMALIZATION_PLAN_JSON,
    )
    args = parser.parse_args()
    packet = run(rune_registry_formalization_plan_path=args.rune_registry_formalization_plan)
    print(packet["terminal_state_id"])
    print(packet["terminal_state_status"])
    print(packet["recommended_next_patch"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
