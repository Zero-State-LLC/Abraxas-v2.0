from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.ingest.outcome_binding_candidate_builder import (  # noqa: E402
    build_brier_readiness_precheck,
    build_outcome_binding_candidate_packet,
    build_resolution_source_requirement_set,
    write_outcome_binding_candidate_outputs,
)


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build advisory-only outcome binding candidates from Oracle intake queue.")
    parser.add_argument("--queue", default="out/ingest/oracle_intake_queue_001.latest.json")
    parser.add_argument("--out", default="out/ingest")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    queue = _read_json(Path(args.queue))
    candidate_packet = build_outcome_binding_candidate_packet(queue)
    requirement_set = build_resolution_source_requirement_set(candidate_packet)
    precheck = build_brier_readiness_precheck(candidate_packet, requirement_set=requirement_set)
    write_outcome_binding_candidate_outputs(
        Path(args.out),
        candidate_packet=candidate_packet,
        requirement_set=requirement_set,
        precheck=precheck,
    )
    print(candidate_packet["candidate_status"])
    print(candidate_packet["candidate_id"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
