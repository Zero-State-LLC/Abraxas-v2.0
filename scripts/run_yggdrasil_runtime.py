from __future__ import annotations

import argparse
from pathlib import Path

from core.runtime.graph_runner import run_execution_graph
from core.yggdrasil.validator import load_route_graph


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pipeline", default="research_intake")
    args = parser.parse_args()
    path = Path(f"contracts/yggdrasil/routes/{args.pipeline}.route.v1.json")
    graph = load_route_graph(path)
    run = run_execution_graph(graph)
    print(run["status"])


if __name__ == "__main__":
    main()
