from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import RuntimePaths
from core.heavy_tail_computation_receipt import (
    build_heavy_tail_computation_receipt,
    validate_heavy_tail_computation_receipt,
)
from core.heavy_tail_fixture_corpus_creation_receipt import (
    build_heavy_tail_fixture_corpus_creation_receipt,
    validate_heavy_tail_fixture_corpus_creation_receipt,
)


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    paths = RuntimePaths.from_env()
    fixture_receipt = build_heavy_tail_fixture_corpus_creation_receipt()
    validate_heavy_tail_fixture_corpus_creation_receipt(fixture_receipt)
    _write_json(paths.heavy_tail_fixture_corpus_creation_receipt_001_latest, fixture_receipt)

    computation_receipt = build_heavy_tail_computation_receipt()
    validate_heavy_tail_computation_receipt(computation_receipt)
    _write_json(paths.heavy_tail_computation_receipt_001_latest, computation_receipt)

    print(
        "heavy_tail_computation_receipt_written",
        paths.heavy_tail_computation_receipt_001_latest,
    )
    print(
        "canonical_hash",
        computation_receipt["canonical_hash"],
    )
    print(
        "recommended_next_step",
        computation_receipt["recommended_next_step"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
