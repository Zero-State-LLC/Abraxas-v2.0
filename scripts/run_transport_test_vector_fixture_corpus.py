"""Runner: create all 15 TRANSPORT test vector fixture files.

Writes each fixture JSON to input/fixtures/transport/{fixture_id}.json.
No metric values emitted. No LP solver invocation. SHADOW lane only.
"""
from __future__ import annotations

import logging
import pathlib
import sys

from core.canonical.json import canonical_dumps
from core.config import RuntimePaths
from core.transport_test_vector_fixture_corpus import (
    ALL_FIXTURE_IDS,
    TransportFixtureCorpusError,
    build_all_fixtures,
    validate_all_fixtures,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)

FIXTURE_BASE_PATH = pathlib.Path("input/fixtures/transport")


def main() -> None:
    _paths = RuntimePaths.from_env()

    log.info("building transport test vector fixture corpus")
    fixtures = build_all_fixtures()
    validate_all_fixtures(fixtures)

    FIXTURE_BASE_PATH.mkdir(parents=True, exist_ok=True)
    log.info("fixture_base_path=%s", FIXTURE_BASE_PATH)

    for fix in fixtures:
        fid = fix["fixture_id"]
        out_path = FIXTURE_BASE_PATH / f"{fid}.json"
        out_path.write_text(canonical_dumps(fix) + "\n")
        log.info(
            "wrote fixture fixture_id=%s fixture_type=%s path=%s",
            fid,
            fix.get("fixture_type"),
            out_path,
        )

    log.info(
        "transport_fixture_corpus_creation_complete fixture_count=%d ids=%s",
        len(fixtures),
        list(ALL_FIXTURE_IDS),
    )


if __name__ == "__main__":
    try:
        main()
    except TransportFixtureCorpusError as exc:
        log.error("fixture_corpus_error: %s", exc)
        sys.exit(1)
