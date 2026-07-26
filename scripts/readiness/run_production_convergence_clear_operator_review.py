#!/usr/bin/env python3
"""Emit advisory CLEAR operator-review packet (no deletion authorization)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_canonical_artifact
from core.production_convergence.clear_operator_review import (
    build_clear_operator_review_packet,
)
from core.production_convergence.clear_reference import build_clear_reference_analysis


def main() -> int:
    # Refresh CLEAR analysis first so the review packet binds a current hash.
    analysis = build_clear_reference_analysis(REPO_ROOT)
    analysis_out = (
        REPO_ROOT / "out/production_convergence/clear_reference_analysis.v1.json"
    )
    write_canonical_artifact(
        analysis_out,
        analysis,
        artifact_class=ArtifactClass.BUILD_EVIDENCE,
        out_root=REPO_ROOT / "out",
    )

    packet = build_clear_operator_review_packet(REPO_ROOT)
    out = REPO_ROOT / "out/production_convergence/clear_operator_review.v1.json"
    write_canonical_artifact(
        out,
        packet,
        artifact_class=ArtifactClass.BUILD_EVIDENCE,
        out_root=REPO_ROOT / "out",
    )
    print(
        json.dumps(
            {
                "ok": True,
                "operator_disposition_status": packet["operator_disposition_status"],
                "mass_deletion_authorized": packet["mass_deletion_authorized"],
                "clear_analysis_output": analysis_out.relative_to(REPO_ROOT).as_posix(),
                "output": out.relative_to(REPO_ROOT).as_posix(),
                "canonical_hash": packet["canonical_hash"],
            },
            sort_keys=True,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
