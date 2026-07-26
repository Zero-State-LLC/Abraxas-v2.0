#!/usr/bin/env python3
"""Advisory check for JSON writes that bypass the classified canonical writer."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_canonical_artifact
from core.production_convergence.writer_bypass import scan_writer_bypasses


def main() -> int:
    report = scan_writer_bypasses(REPO_ROOT)
    out = REPO_ROOT / "out/production_convergence/canonical_writer_bypass_advisory.v1.json"
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
                "mode": "advisory",
                "finding_count": report["summary"]["finding_count"],
                "output": out.relative_to(REPO_ROOT).as_posix(),
            },
            sort_keys=True,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
