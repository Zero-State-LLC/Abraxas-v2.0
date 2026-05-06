from core.runtime.graph_runner import run_execution_graph
from core.yggdrasil.validator import load_route_graph


def test_runtime_run_completed() -> None:
    run = run_execution_graph(load_route_graph("contracts/yggdrasil/routes/research_intake.route.v1.json"))
    assert run["schema_version"] == "YggdrasilRuntimeRun.v1"
    assert "graph" in run
