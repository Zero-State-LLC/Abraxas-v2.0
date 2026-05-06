from core.yggdrasil.runtime import build_execution_graph
from core.yggdrasil.scheduler import schedule_execution_graph
from core.yggdrasil.validator import load_route_graph


def test_scheduler_deterministic() -> None:
    graph = build_execution_graph(load_route_graph("contracts/yggdrasil/routes/research_intake.route.v1.json"))
    s1 = schedule_execution_graph(graph)
    s2 = schedule_execution_graph(graph)
    assert s1.scheduler_id == s2.scheduler_id
