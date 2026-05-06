from core.overlay_topology.replay import OverlayTopologyReplayPacket

def test_replay_match():
 p=OverlayTopologyReplayPacket(replay_id='1',source_graph_hash='a',replay_graph_hash='a',deterministic_match=True,mismatched_components=[],status='passed')
 assert p.deterministic_match
