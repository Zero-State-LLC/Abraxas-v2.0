"""Runner: emit TransportFixtureCorpusCreationReceipt.v1 artifact.

Reads all 15 fixture files from disk, verifies hashes, and writes the
receipt to out/metric_operator/. Requires fixture files to already exist.
No metric values emitted. No LP solver invocation. SHADOW lane only.
"""
from __future__ import annotations

import logging
import pathlib
import sys

from core.canonical.json import canonical_dumps
from core.config import RuntimePaths
from core.transport_fixture_corpus_creation_receipt import (
    TransportFixtureCorpusCreationReceiptError,
    build_transport_fixture_corpus_creation_receipt,
    validate_transport_fixture_corpus_creation_receipt,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)

OUT_PATH = pathlib.Path(
    "out/metric_operator/"
    "transport_fixture_corpus_creation_receipt_001.latest.json"
)


def main() -> None:
    _paths = RuntimePaths.from_env()

    log.info("building transport fixture corpus creation receipt")
    receipt = build_transport_fixture_corpus_creation_receipt()
    validate_transport_fixture_corpus_creation_receipt(receipt)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(canonical_dumps(receipt) + "\n")

    log.info(
        "receipt_written receipt_id=%s receipt_status=%s "
        "fixture_count_total=%d canonical_hash=%s path=%s",
        receipt["receipt_id"],
        receipt["receipt_status"],
        receipt["fixture_count_total"],
        receipt["canonical_hash"],
        OUT_PATH,
    )
    log.info("recommended_next_step=%s", receipt.get("recommended_next_step"))


if __name__ == "__main__":
    try:
        main()
    except TransportFixtureCorpusCreationReceiptError as exc:
        log.error("receipt_error: %s", exc)
        sys.exit(1)
