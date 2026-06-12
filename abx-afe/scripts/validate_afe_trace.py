from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from afe.cli import validate_trace_packet  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate an AFETracePacket.v1 JSON file.")
    parser.add_argument("packet", type=Path)
    args = parser.parse_args()
    validate_trace_packet(json.loads(args.packet.read_text(encoding="utf-8")))
    print("AFE_TRACE_VALID")


if __name__ == "__main__":
    main()

