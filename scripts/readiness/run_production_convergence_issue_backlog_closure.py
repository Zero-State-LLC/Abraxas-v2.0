#!/usr/bin/env python3
"""Emit advisory issue-backlog closure receipt for Production Convergence."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_classified_json
from core.production_convergence.issue_backlog_closure import (
    build_issue_backlog_closure_receipt,
)

_OUT = Path("out/production_convergence/issue_backlog_closure.v1.json")
_OUT_ROOT = Path("out")


def main() -> None:
    payload = build_issue_backlog_closure_receipt()
    _OUT.parent.mkdir(parents=True, exist_ok=True)
    write_classified_json(
        _OUT,
        payload,
        artifact_class=ArtifactClass.BUILD_EVIDENCE,
        out_root=_OUT_ROOT,
    )
    print(json.dumps({"output": str(_OUT), "canonical_hash": payload["canonical_hash"]}))


if __name__ == "__main__":
    main()
