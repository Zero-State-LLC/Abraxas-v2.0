#!/usr/bin/env python3
"""Sole-writer for yggdrasil runtime execution graph (WP-D4-C4)."""
from __future__ import annotations

import argparse
from pathlib import Path

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_classified_json
from core.runtime.graph_runner import run_execution_graph
from core.yggdrasil.validator import load_route_graph

_OUT_ROOT = Path('out')

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--pipeline', default='research_intake')
    args = parser.parse_args()
    path = Path(f'contracts/yggdrasil/routes/{args.pipeline}.route.v1.json')
    graph = load_route_graph(path)
    run = run_execution_graph(graph)
    write_classified_json('out/yggdrasil/runtime.latest.json', run, artifact_class=ArtifactClass.RUNTIME_EVENT, out_root=_OUT_ROOT)
    write_classified_json('out/yggdrasil/receipt.latest.json', run['receipt'], artifact_class=ArtifactClass.AUDIT_EVIDENCE, out_root=_OUT_ROOT)
    write_classified_json('out/route_cache/latest.json', run['cache'], artifact_class=ArtifactClass.AUDIT_EVIDENCE, out_root=_OUT_ROOT)
    print(run['status'])
if __name__ == '__main__':
    main()
