"""Runner: emit TransportFixtureCorpusCreationPlan.v1 artifact."""
from __future__ import annotations

import json
import logging
import sys

from core.config import RuntimePaths
from core.transport_fixture_corpus_creation_plan import (
    TransportFixtureCorpusCreationPlanValidationError,
    build_transport_fixture_corpus_creation_plan,
    validate_transport_fixture_corpus_creation_plan,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)


def main() -> None:
    paths = RuntimePaths.from_env()
    out_path = paths.transport_fixture_corpus_creation_plan_001_latest

    log.info("Building TransportFixtureCorpusCreationPlan.v1 ...")
    plan = build_transport_fixture_corpus_creation_plan()

    log.info("Validating ...")
    try:
        validate_transport_fixture_corpus_creation_plan(plan)
    except TransportFixtureCorpusCreationPlanValidationError as exc:
        log.error("Validation failed: %s", exc)
        sys.exit(1)

    fpp = plan["fixture_path_plan"]
    log.info(
        "Fixture corpus: total=%d  valid=%d  invalid=%d  not_computable=%d  base=%s",
        fpp["fixture_count"],
        fpp["valid_fixture_count"],
        fpp["invalid_fixture_count"],
        fpp["not_computable_fixture_count"],
        fpp["base_path"],
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(plan, indent=4) + "\n")
    log.info(
        "Wrote %s  canonical_hash=%s  status=%s",
        out_path,
        plan["canonical_hash"][:16] + "...",
        plan["plan_status"],
    )
    print(f"plan_status={plan['plan_status']}")
    print(f"canonical_hash={plan['canonical_hash']}")
    print(f"recommended_next_step={plan['recommended_next_step']}")
    print(f"wrote={out_path.as_posix()}")


if __name__ == "__main__":
    main()
