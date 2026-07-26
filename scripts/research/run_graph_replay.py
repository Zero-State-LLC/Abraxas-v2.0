#!/usr/bin/env python3
"""Sole-writer for graph replay packet (TD Wave 1)."""

from __future__ import annotations

import json
from pathlib import Path

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_classified_json
from core.runtime.topology_replay import replay_execution_graph

_OUT_ROOT = Path("out")


def main() -> None:
    runtime_run = json.loads(
        Path("out/yggdrasil/runtime.latest.json").read_text(encoding="utf-8")
    )
    packet = replay_execution_graph(runtime_run)
    write_classified_json(
        "out/graph_replay/latest.json",
        packet,
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=_OUT_ROOT,
    )
    print(packet["status"])


if __name__ == "__main__":
    main()
