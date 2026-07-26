#!/usr/bin/env python3
"""Emit advisory CLEAR-phase reference analysis (no deletions)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_canonical_artifact
from core.production_convergence.clear_reference import build_clear_reference_analysis


def main() -> int:
    report = build_clear_reference_analysis(REPO_ROOT)
    out = REPO_ROOT / "out/production_convergence/clear_reference_analysis.v1.json"
    write_canonical_artifact(
        out,
        report,
        artifact_class=ArtifactClass.BUILD_EVIDENCE,
        out_root=REPO_ROOT / "out",
    )
    print(
        json.dumps(
            {
                "ok": True,
                "mass_deletion_authorized": report["mass_deletion_authorized"],
                "entry_count": report["summary"]["entry_count"],
                "output": out.relative_to(REPO_ROOT).as_posix(),
                "canonical_hash": report["canonical_hash"],
            },
            sort_keys=True,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
