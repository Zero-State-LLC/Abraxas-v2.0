"""Script: emit deterministic ChamferBaselinePromotionComplete.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.chamfer_baseline_promotion_complete import (
    build_chamfer_baseline_promotion_complete,
    validate_chamfer_baseline_promotion_complete,
)
from core.canonical.json import canonical_dumps
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH_CHAMFER_SHADOW_STUB_BASELINE_PROMOTION_COMPLETE_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.chamfer_baseline_promotion_complete_001_latest


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "chamfer_baseline_promotion_complete",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "chamfer_baseline_promotion_complete_started",
        patch_id=PATCH_ID,
        correlation_id=correlation_id,
        out_path=str(OUT_PATH),
    )

    doc = build_chamfer_baseline_promotion_complete()
    validate_chamfer_baseline_promotion_complete(doc)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(canonical_dumps(doc) + "\n", encoding="utf-8")

    log_event(
        logger,
        "INFO",
        "chamfer_baseline_promotion_complete_written",
        patch_id=PATCH_ID,
        correlation_id=correlation_id,
        out_path=str(OUT_PATH),
        canonical_hash=doc["canonical_hash"],
        complete_status=doc["complete_status"],
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
