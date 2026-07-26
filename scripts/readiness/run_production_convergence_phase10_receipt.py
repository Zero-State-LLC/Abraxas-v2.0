#!/usr/bin/env python3
"""Emit Phase 10 production-convergence writer-migration receipt."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_canonical_artifact
from core.production_convergence.phase10 import build_phase10_writer_migration_receipt


def main() -> int:
    receipt = build_phase10_writer_migration_receipt()
    out = REPO_ROOT / "out/production_convergence/phase10_writer_migration.v1.json"
    write_canonical_artifact(
        out,
        receipt,
        artifact_class=ArtifactClass.BUILD_EVIDENCE,
        out_root=REPO_ROOT / "out",
    )
    print(
        json.dumps(
            {
                "ok": True,
                "migrated_count": receipt["summary"]["migrated_count"],
                "output": out.relative_to(REPO_ROOT).as_posix(),
                "canonical_hash": receipt["canonical_hash"],
            },
            sort_keys=True,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
