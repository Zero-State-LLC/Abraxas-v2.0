#!/usr/bin/env python3
"""Runner: emit GeodesicExpectedValuesAdditionReceipt.v1 artifact."""
from __future__ import annotations

import json
import logging
import sys

from core.config import RuntimePaths
from core.geodesic_expected_values_addition_receipt import (
    GeodesicExpectedValuesAdditionReceiptValidationError,
    build_addition_receipt,
    validate_addition_receipt,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)


def main() -> None:
    paths = RuntimePaths.from_env()
    out_path = paths.geodesic_expected_values_addition_receipt_latest

    log.info("Building GeodesicExpectedValuesAdditionReceipt.v1 ...")
    receipt = build_addition_receipt()

    log.info("Validating ...")
    try:
        validate_addition_receipt(receipt)
    except GeodesicExpectedValuesAdditionReceiptValidationError as exc:
        log.error("Validation failed: %s", exc)
        sys.exit(1)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(receipt, indent=4) + "\n")
    log.info(
        "Wrote %s  canonical_hash=%s  status=%s",
        out_path,
        receipt["canonical_hash"][:16] + "…",
        receipt["receipt_status"],
    )


if __name__ == "__main__":
    main()
