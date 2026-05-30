"""Runner: TRANSPORT COMPUTATION — BOUNDED SHADOW TEST-VECTOR COMPUTATION.

Algorithm: DETERMINISTIC_ENUMERATED_BASIC_FEASIBLE_SEARCH
Lane:      SHADOW (test vectors only)
Scope:     TEST_VECTOR_COMPUTATION_ONLY
Output:    out/metric_operator/transport_computation_receipt_001.latest.json
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

from core.config import RuntimePaths
from core.transport_computation import (
    TransportComputationError,
    build_transport_computation_receipt,
    validate_transport_computation_receipt,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)

FIXTURE_DIR = Path("input/fixtures/transport")
OUT_PATH = Path("out/metric_operator/transport_computation_receipt_001.latest.json")


def _load_corpus_manifest() -> list[dict]:
    paths = RuntimePaths.from_env()
    corpus = json.loads(
        paths.transport_fixture_corpus_creation_receipt_001_latest.read_text()
    )
    return corpus["fixture_manifest"]


def main() -> None:
    log.info("TRANSPORT COMPUTATION — BOUNDED SHADOW TEST-VECTOR COMPUTATION")
    log.info("Algorithm: DETERMINISTIC_ENUMERATED_BASIC_FEASIBLE_SEARCH")
    log.info("Lane: SHADOW | Scope: TEST_VECTOR_COMPUTATION_ONLY")

    manifest = _load_corpus_manifest()
    log.info("Loaded corpus manifest: %d fixtures", len(manifest))

    receipt = build_transport_computation_receipt(FIXTURE_DIR, manifest)

    log.info("Validating receipt ...")
    try:
        validate_transport_computation_receipt(receipt)
    except TransportComputationError as exc:
        log.error("Validation failed: %s", exc)
        sys.exit(1)

    counts = {
        "total": receipt["fixture_count_total"],
        "valid": receipt["fixture_count_valid"],
        "invalid": receipt["fixture_count_invalid"],
        "nc": receipt["fixture_count_not_computable"],
    }
    log.info(
        "Fixtures: total=%d valid=%d invalid=%d not_computable=%d",
        counts["total"], counts["valid"], counts["invalid"], counts["nc"],
    )
    log.info(
        "Results: all_valid_passed=%s all_invalid_rejected=%s all_nc_routed=%s",
        receipt["all_valid_passed"],
        receipt["all_invalid_rejected"],
        receipt["all_not_computable_routed"],
    )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(receipt, indent=4) + "\n")

    log.info(
        "Wrote %s  canonical_hash=%s  status=%s",
        OUT_PATH,
        receipt["canonical_hash"][:16] + "...",
        receipt["receipt_status"],
    )

    print(f"receipt_status={receipt['receipt_status']}")
    print(f"all_matched={receipt['all_matched']}")
    print(f"canonical_hash={receipt['canonical_hash']}")
    print(f"wrote={OUT_PATH.as_posix()}")


if __name__ == "__main__":
    main()
