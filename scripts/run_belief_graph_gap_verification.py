from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.belief_graph_gap_verification import (  # noqa: E402
    OUT_JSON,
    OUT_MD,
    build_belief_graph_gap_verification,
    write_belief_graph_gap_verification,
    write_belief_graph_gap_verification_markdown,
)


def run(
    *,
    repo_root: str | Path = ROOT,
    out_json: str | Path | None = None,
    out_md: str | Path | None = None,
) -> dict:
    root = Path(repo_root)
    packet = build_belief_graph_gap_verification(repo_root=root)
    json_target = root / (Path(out_json) if out_json is not None else Path(OUT_JSON))
    md_target = root / (Path(out_md) if out_md is not None else Path(OUT_MD))
    write_belief_graph_gap_verification(json_target, packet)
    write_belief_graph_gap_verification_markdown(md_target, packet)
    return packet


def main() -> int:
    packet = run()
    print(packet["verification_id"])
    print(packet["verification_status"])
    print(packet["recommended_next_patch"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
