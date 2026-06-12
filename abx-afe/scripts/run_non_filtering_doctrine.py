from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from jsonschema import validate

from afe.non_filtering_doctrine import build_non_filtering_doctrine_packet

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "AFENonFilteringObservationDoctrine.v1.json"


def run(out_path: Path | None = None) -> dict[str, Any]:
    packet = build_non_filtering_doctrine_packet()
    validate_non_filtering_doctrine(packet)
    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return packet


def validate_non_filtering_doctrine(packet: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    validate(packet, schema)


def main() -> None:
    parser = argparse.ArgumentParser(description="Emit AFE observation-only non-filtering doctrine packet.")
    parser.add_argument("--out", type=Path, default=ROOT / "out" / "afe_non_filtering_doctrine.latest.json")
    args = parser.parse_args()
    packet = run(args.out)
    print(f"AUTHORITY: {packet['authority']}")
    print(f"OUTPUT_EFFECT: {packet['output_effect']}")
    print(f"NON_FILTERING_COMPLIANCE: {packet['non_filtering_compliance']}")
    print(f"DOCTRINE: {args.out}")


if __name__ == "__main__":
    main()
