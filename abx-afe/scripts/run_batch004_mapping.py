from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from jsonschema import validate

from afe.real_world_mapping import build_batch004_mapping_packet

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "AFERealWorldMappingBatch.v1.json"


def run(out_path: Path | None = None) -> dict[str, Any]:
    packet = build_batch004_mapping_packet()
    validate_batch004_mapping(packet)
    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return packet


def validate_batch004_mapping(packet: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    validate(packet, schema)


def main() -> None:
    parser = argparse.ArgumentParser(description="Emit AFE Batch 004 annotation-only mapping.")
    parser.add_argument("--out", type=Path, default=ROOT / "out" / "afe_batch004_mapping.latest.json")
    args = parser.parse_args()
    packet = run(args.out)
    print(f"STATUS: {packet['output_effect']}")
    print(f"AUTHORITY: {packet['authority']}")
    print(f"LIVE_INGESTION_PERFORMED: {packet['live_ingestion_performed']}")
    print(f"BATCH004_MAPPING: {args.out}")


if __name__ == "__main__":
    main()
