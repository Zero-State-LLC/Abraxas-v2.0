from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from jsonschema import validate

from afe.batch import build_hybrid_batch

ROOT = Path(__file__).resolve().parents[1]
BATCH_SCHEMA = ROOT / "schemas" / "AFEHybridBatch.v1.json"


def run(
    *,
    batch_id: str,
    runs: int,
    seed_start: int,
    environment_set: str,
    export_target: str,
    out_path: Path | None = None,
) -> dict[str, Any]:
    packet = build_hybrid_batch(
        batch_id=batch_id,
        runs=runs,
        seed_start=seed_start,
        environment_set=environment_set.split(","),
        export_target=export_target,
    )
    validate_hybrid_batch(packet)
    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return packet


def validate_hybrid_batch(packet: dict[str, Any]) -> None:
    schema = json.loads(BATCH_SCHEMA.read_text(encoding="utf-8"))
    validate(packet, schema)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run an AFE v0.3 SHADOW-only hybrid batch.")
    parser.add_argument("--batch-id", required=True)
    parser.add_argument("--runs", type=int, required=True)
    parser.add_argument("--seed-start", type=int, required=True)
    parser.add_argument("--environment-set", required=True)
    parser.add_argument("--export", choices=("json", "notion"), default="json", dest="export_target")
    parser.add_argument("--out", type=Path, default=ROOT / "out" / "afe_hybrid_batch.latest.json")
    args = parser.parse_args()
    packet = run(
        batch_id=args.batch_id,
        runs=args.runs,
        seed_start=args.seed_start,
        environment_set=args.environment_set,
        export_target=args.export_target,
        out_path=args.out,
    )
    print(f"STATUS: {packet['status']}")
    print(f"AUTHORITY: {packet['authority']}")
    print(f"LIVE_NOTION_WRITEBACK: {packet['live_notion_writeback']}")
    print(f"HYBRID_BATCH: {args.out}")


if __name__ == "__main__":
    main()
