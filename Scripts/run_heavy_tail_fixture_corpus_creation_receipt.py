"""Runner: materialize the Heavy Tail fixture corpus and emit its receipt."""
from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.canonical.json import canonical_dumps
from core.config import RuntimePaths
from core.heavy_tail_fixture_corpus_creation_receipt import (
    HeavyTailFixtureCorpusCreationReceiptError,
    build_heavy_tail_fixture_corpus_creation_receipt,
    materialize_heavy_tail_fixture_corpus,
    validate_heavy_tail_fixture_corpus_creation_receipt,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)


def main() -> None:
    paths = RuntimePaths.from_env()
    out_path = paths.heavy_tail_fixture_corpus_creation_receipt_001_latest

    log.info("materializing heavy tail fixture corpus")
    documents = materialize_heavy_tail_fixture_corpus()

    log.info("building heavy tail fixture corpus creation receipt")
    receipt = build_heavy_tail_fixture_corpus_creation_receipt()
    validate_heavy_tail_fixture_corpus_creation_receipt(receipt)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(canonical_dumps(receipt) + "\n", encoding="utf-8")

    log.info(
        "receipt_written receipt_id=%s receipt_status=%s fixture_count_total=%d canonical_hash=%s path=%s",
        receipt["receipt_id"],
        receipt["receipt_status"],
        receipt["fixture_count_total"],
        receipt["canonical_hash"],
        out_path,
    )
    log.info("fixture_files_written=%d", len(documents))
    log.info("recommended_next_step=%s", receipt.get("recommended_next_step"))


if __name__ == "__main__":
    try:
        main()
    except HeavyTailFixtureCorpusCreationReceiptError as exc:
        log.error("receipt_error: %s", exc)
        sys.exit(1)
