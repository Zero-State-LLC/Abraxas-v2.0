"""Script: emit deterministic GeodesicBaselinePromotionComplete.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.geodesic_baseline_promotion_complete import (
    build_geodesic_baseline_promotion_complete,
    validate_geodesic_baseline_promotion_complete,
)
from core.canonical.json import canonical_dumps
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH_GEODESIC_SHADOW_STUB_BASELINE_PROMOTION_COMPLETE_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.geodesic_baseline_promotion_complete_latest


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "geodesic_baseline_promotion_complete",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "geodesic_baseline_promotion_complete_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    doc = build_geodesic_baseline_promotion_complete()
    validate_geodesic_baseline_promotion_complete(doc)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(canonical_dumps(doc) + "\n", encoding="utf-8")

    log_event(
        logger,
        "INFO",
        "geodesic_baseline_promotion_complete_finished",
        artifact_path=OUT_PATH.as_posix(),
        complete_status=doc.get("complete_status", "?"),
        canonical_hash=doc.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"complete_id={doc['complete_id']}")
    print(f"complete_status={doc['complete_status']}")
    print(f"canonical_hash={doc.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
