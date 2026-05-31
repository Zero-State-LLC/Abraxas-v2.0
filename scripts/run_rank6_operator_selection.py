"""Script: emit deterministic Rank6OperatorSelection.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.rank6_operator_selection import (
    build_rank6_operator_selection,
    validate_rank6_operator_selection,
)
from core.canonical.json import canonical_dumps
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH_RANK6_OPERATOR_SELECTION_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.rank6_operator_selection_001_latest


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "rank6_operator_selection",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "rank6_operator_selection_started",
        patch_id=PATCH_ID,
        correlation_id=correlation_id,
        out_path=str(OUT_PATH),
    )

    doc = build_rank6_operator_selection()
    validate_rank6_operator_selection(doc)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(canonical_dumps(doc) + "\n", encoding="utf-8")

    log_event(
        logger,
        "INFO",
        "rank6_operator_selection_written",
        patch_id=PATCH_ID,
        correlation_id=correlation_id,
        out_path=str(OUT_PATH),
        canonical_hash=doc["canonical_hash"],
        selected_operator=doc["selected_rank6_operator"]["operator_id"],
        selection_status=doc["selection_status"],
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
