from core.runtime.graph_runner import run_execution_graph
from core.runtime.topology_replay import replay_execution_graph
from core.yggdrasil.validator import load_route_graph


def test_graph_replay_packet() -> None:
    run = run_execution_graph(load_route_graph("contracts/yggdrasil/routes/research_intake.route.v1.json"))
    packet = replay_execution_graph(run)
    assert packet["schema_version"] == "GraphReplayPacket.v1"
