#!/usr/bin/env python3
"""Emit Phase 14 receipt + CLEAR disposition draft (no deletions / no canary regen)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_canonical_artifact
from core.production_convergence.clear_disposition_draft import (
    build_clear_disposition_draft,
)
from core.production_convergence.clear_operator_review import (
    build_clear_operator_review_packet,
)
from core.production_convergence.clear_reference import build_clear_reference_analysis
from core.production_convergence.phase14 import build_phase14_receipt


def _write(rel: str, payload: dict) -> str:
    out = REPO_ROOT / rel
    write_canonical_artifact(
        out,
        payload,
        artifact_class=ArtifactClass.BUILD_EVIDENCE,
        out_root=REPO_ROOT / "out",
    )
    return out.relative_to(REPO_ROOT).as_posix()


def main() -> int:
    # Refresh CLEAR analysis (consumes Phase 13) then draft + operator review.
    analysis = build_clear_reference_analysis(REPO_ROOT)
    analysis_out = _write(
        "out/production_convergence/clear_reference_analysis.v1.json", analysis
    )
    draft = build_clear_disposition_draft(REPO_ROOT)
    draft_out = _write(
        "out/production_convergence/clear_disposition_draft.v1.json", draft
    )
    review = build_clear_operator_review_packet(REPO_ROOT)
    review_out = _write(
        "out/production_convergence/clear_operator_review.v1.json", review
    )
    receipt = build_phase14_receipt()
    receipt_out = _write(
        "out/production_convergence/phase14_clear_disposition_and_canary_writer.v1.json",
        receipt,
    )
    print(
        json.dumps(
            {
                "ok": True,
                "migrated_count": receipt["summary"]["migrated_count"],
                "mass_deletion_authorized": False,
                "deletions_executed": False,
                "engineering_disposition_status": draft["engineering_disposition_status"],
                "operator_disposition_status": review["operator_disposition_status"],
                "outputs": {
                    "analysis": analysis_out,
                    "disposition_draft": draft_out,
                    "operator_review": review_out,
                    "phase14_receipt": receipt_out,
                },
                "canonical_hash": receipt["canonical_hash"],
            },
            sort_keys=True,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
