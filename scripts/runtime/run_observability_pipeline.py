#!/usr/bin/env python3
"""Sole-writer for observability aggregation (WP-D4-C3)."""

from __future__ import annotations

import json
from pathlib import Path

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_classified_json
from core.observability.aggregation import run_observability_pipeline

_OUT_ROOT = Path("out")


def _load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> None:
    execution = (
        _load("out/execution/latest.json")
        if Path("out/execution/latest.json").exists()
        else {}
    )
    replay = (
        _load("out/graph_replay/latest.json")
        if Path("out/graph_replay/latest.json").exists()
        else {}
    )
    graph = (
        _load("out/yggdrasil/runtime.latest.json")
        if Path("out/yggdrasil/runtime.latest.json").exists()
        else {}
    )
    if Path("out/projections/aal_viz.latest.json").exists():
        execution["projection"] = _load("out/projections/aal_viz.latest.json")
    if Path("out/operator_review/latest.json").exists():
        execution["queue"] = _load("out/operator_review/latest.json")
    if Path("out/validation/latest.json").exists():
        execution["validation"] = _load("out/validation/latest.json")
    agg = run_observability_pipeline(execution, replay, graph)
    write_classified_json(
        "out/observability/latest.json",
        agg,
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=_OUT_ROOT,
    )
    write_classified_json(
        "out/lineage/latest.json",
        agg["lineage"],
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=_OUT_ROOT,
    )
    write_classified_json(
        "out/timelines/latest.json",
        agg["timeline"],
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=_OUT_ROOT,
    )
    write_classified_json(
        "out/telemetry/latest.json",
        agg["telemetry"],
        artifact_class=ArtifactClass.RUNTIME_EVENT,
        out_root=_OUT_ROOT,
    )
    print(agg["status"])


if __name__ == "__main__":
    main()
