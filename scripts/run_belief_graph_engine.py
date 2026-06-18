from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.belief_graph_engine import build_belief_graph_engine_packet  # noqa: E402
from core.canonical.json import write_canonical_json  # noqa: E402

OUT_JSON = Path("out/belief_graph/belief_graph_engine_001.latest.json")


def run(
    *,
    repo_root: str | Path = ROOT,
    out_json: str | Path | None = None,
) -> dict[str, object]:
    root = Path(repo_root)
    packet = build_belief_graph_engine_packet([])
    target = root / (Path(out_json) if out_json is not None else OUT_JSON)
    write_canonical_json(target, packet)
    return packet


def main() -> int:
    packet = run()
    print(packet["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
