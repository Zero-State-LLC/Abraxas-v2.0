from __future__ import annotations

import json
from pathlib import Path

from core.observability.aggregation import run_observability_pipeline


def _load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> None:
    execution = _load("out/execution/latest.json") if Path("out/execution/latest.json").exists() else {}
    replay = _load("out/graph_replay/latest.json")
    graph = _load("out/yggdrasil/runtime.latest.json")
    if Path("out/projections/aal_viz.latest.json").exists():
        execution["projection"] = _load("out/projections/aal_viz.latest.json")
    if Path("out/operator_review/latest.json").exists():
        execution["queue"] = _load("out/operator_review/latest.json")
    if Path("out/validation/latest.json").exists():
        execution["validation"] = _load("out/validation/latest.json")
    agg = run_observability_pipeline(execution, replay, graph)
    print(agg["status"])


if __name__ == "__main__":
    main()
