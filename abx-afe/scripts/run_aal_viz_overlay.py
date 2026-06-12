from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from jsonschema import validate

from afe.aal_viz_overlay import build_aal_viz_overlay_packet

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "AFEAALVizOverlayPacket.v1.json"


def run(out_path: Path | None = None) -> dict[str, Any]:
    packet = build_aal_viz_overlay_packet()
    validate_aal_viz_overlay(packet)
    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return packet


def validate_aal_viz_overlay(packet: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    validate(packet, schema)


def main() -> None:
    parser = argparse.ArgumentParser(description="Emit AFE projection-only AAL-Viz overlay packet.")
    parser.add_argument("--out", type=Path, default=ROOT / "out" / "afe_aal_viz_overlay.latest.json")
    args = parser.parse_args()
    packet = run(args.out)
    print(f"AUTHORITY: {packet['authority']}")
    print(f"OUTPUT_EFFECT: {packet['output_effect']}")
    print(f"MAX_OVERLAY_OPACITY: {packet['rendering_locks']['max_overlay_opacity']}")
    print(f"AAL_VIZ_OVERLAY: {args.out}")


if __name__ == "__main__":
    main()
