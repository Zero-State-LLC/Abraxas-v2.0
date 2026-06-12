from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from jsonschema import validate

from afe.batch import build_hybrid_batch
from afe.oracle_annotation import attach_annotation_to_oracle_output, build_oracle_annotation
from afe.real_world_mapping import build_batch004_mapping_packet

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "AFEOracleAnnotation.v1.json"


def run(out_path: Path | None = None) -> dict[str, Any]:
    hybrid = build_hybrid_batch(
        batch_id="AFE-BATCH-001",
        runs=3,
        seed_start=42,
        environment_set=("baseline", "scarcity", "high-noise"),
        export_target="json",
    )
    annotation = build_oracle_annotation(
        trace_packets=hybrid["agent_trace_intake_export"]["trace_packets"],
        batch004_packet=build_batch004_mapping_packet(),
    )
    validate_oracle_annotation(annotation)
    attached = attach_annotation_to_oracle_output(
        {"text": "Oracle output remains intact.", "mode": "shadow_review"},
        annotation,
    )
    packet = {"annotation": annotation, "attached_output": attached}
    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return packet


def validate_oracle_annotation(annotation: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    validate(annotation, schema)


def main() -> None:
    parser = argparse.ArgumentParser(description="Emit AFE annotation-only Oracle observation panel.")
    parser.add_argument("--out", type=Path, default=ROOT / "out" / "afe_oracle_annotation.latest.json")
    args = parser.parse_args()
    packet = run(args.out)
    observation = packet["annotation"]["afe_observation"]
    print(f"AUTHORITY: {observation['authority']}")
    print(f"OUTPUT_EFFECT: {observation['output_effect']}")
    print(f"NON_FILTERING_COMPLIANCE: {observation['non_filtering_compliance']}")
    print(f"ORACLE_ANNOTATION: {args.out}")


if __name__ == "__main__":
    main()
