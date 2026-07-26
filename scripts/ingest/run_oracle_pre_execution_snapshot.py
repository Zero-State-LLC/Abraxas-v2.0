#!/usr/bin/env python3
"""Sole-writer for oracle pre-execution snapshot (TD Wave 1)."""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from core.abraxas_oracle_pre_execution_snapshot import snapshot
from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_classified_json

_OUT_ROOT = Path('out')

def main() -> None:
    snap = snapshot()
    out = Path('out/oracle_execution/pre_execution_snapshot.v1.json')
    out.parent.mkdir(parents=True, exist_ok=True)
    write_classified_json(out, snap, artifact_class=ArtifactClass.AUDIT_EVIDENCE, out_root=_OUT_ROOT)
    print('Snapshot written.')
if __name__ == '__main__':
    main()
