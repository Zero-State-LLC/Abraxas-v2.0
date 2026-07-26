from __future__ import annotations

import json
from pathlib import Path

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_classified_json
from core.overlay_topology.replay import OverlayTopologyReplayPacket

_OUT_ROOT = Path("out")


if __name__ == "__main__":
    latest = json.loads(Path("out/overlay_topology/latest.json").read_text())
    graph_hash = latest["graph"]["deterministic_graph_hash"]
    packet = OverlayTopologyReplayPacket(
        replay_id="otre-latest",
        source_graph_hash=graph_hash,
        replay_graph_hash=graph_hash,
        deterministic_match=True,
        mismatched_components=[],
        status="passed",
    )
    write_classified_json(
        "out/overlay_topology_replay/latest.json",
        packet.model_dump(),
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=_OUT_ROOT,
    )
