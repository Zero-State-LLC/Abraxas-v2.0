#!/usr/bin/env python3
"""LOCAL_DEV recovery drill for the supported advisory spine (Phase 7)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_canonical_artifact
from core.production_convergence.recovery_drill import run_recovery_drill


def main() -> int:
    task = json.loads(
        (REPO_ROOT / "fixtures/alembic/example_task.json").read_text(encoding="utf-8")
    )
    work_dir = REPO_ROOT / "out/production_convergence/recovery_drill_workspace"
    report = run_recovery_drill(
        repo_root=REPO_ROOT,
        work_dir=work_dir,
        alembic_task=task,
    )
    out = REPO_ROOT / "out/production_convergence/recovery_drill_report.v1.json"
    write_canonical_artifact(
        out,
        {
            "artifact_type": "production_convergence_recovery_drill_report",
            "schema_version": "recovery_drill_report.v1",
            **report,
        },
        artifact_class=ArtifactClass.BUILD_EVIDENCE,
        out_root=REPO_ROOT / "out",
    )
    print(json.dumps({"ok": report["status"] == "OK", "report": report}, sort_keys=True))
    return 0 if report["status"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
