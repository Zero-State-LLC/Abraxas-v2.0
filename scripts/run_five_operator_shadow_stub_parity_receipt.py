"""Script: emit deterministic FiveOperatorShadowStubParityReceipt.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.five_operator_shadow_stub_parity_receipt import (
    build_five_operator_shadow_stub_parity_receipt,
    validate_five_operator_shadow_stub_parity_receipt,
)
from core.canonical.json import canonical_dumps
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH_FIVE_OPERATOR_SHADOW_STUB_PARITY_RECEIPT_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.five_operator_shadow_stub_parity_receipt_001_latest


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "five_operator_shadow_stub_parity_receipt",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "five_operator_shadow_stub_parity_receipt_started",
        patch_id=PATCH_ID,
        correlation_id=correlation_id,
        out_path=str(OUT_PATH),
    )

    doc = build_five_operator_shadow_stub_parity_receipt()
    validate_five_operator_shadow_stub_parity_receipt(doc)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(canonical_dumps(doc) + "\n", encoding="utf-8")

    log_event(
        logger,
        "INFO",
        "five_operator_shadow_stub_parity_receipt_written",
        patch_id=PATCH_ID,
        correlation_id=correlation_id,
        out_path=str(OUT_PATH),
        canonical_hash=doc["canonical_hash"],
        receipt_status=doc["receipt_status"],
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
