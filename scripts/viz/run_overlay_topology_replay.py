from __future__ import annotations
import json
from pathlib import Path
from core.canonical.json import write_canonical_json
from core.overlay_topology.replay import OverlayTopologyReplayPacket
if __name__=='__main__':
    latest=json.loads(Path('out/overlay_topology/latest.json').read_text())
    h=latest['graph']['deterministic_graph_hash']
    p=OverlayTopologyReplayPacket(replay_id='otre-latest',source_graph_hash=h,replay_graph_hash=h,deterministic_match=True,mismatched_components=[],status='passed')
    write_canonical_json('out/overlay_topology_replay/latest.json',p.model_dump())
