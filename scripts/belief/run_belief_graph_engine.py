from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.belief_graph_engine import build_belief_graph_engine_packet
from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import infer_out_root, write_classified_json

OUT_JSON = Path("out/belief_graph/belief_graph_engine_001.latest.json")


def run(
    *,
    repo_root: str | Path = ROOT,
    out_json: str | Path | None = None,
) -> dict[str, object]:
    root = Path(repo_root)
    packet = build_belief_graph_engine_packet([])
    target = root / (Path(out_json) if out_json is not None else OUT_JSON)
    write_classified_json(
        target,
        packet,
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=infer_out_root(target, fallback=root / "out"),
    )
    return packet


def main() -> int:
    packet = run()
    print(packet["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
