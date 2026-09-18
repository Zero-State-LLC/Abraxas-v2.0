#!/usr/bin/env python3
"""SHADOW runner: intent → ForgeIngestEnvelope.v1 (no canon / forecast / plaintext)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
_SKILL = _REPO / "skills" / "abx-esoteric-intelligence"
sys.path.insert(0, str(_SKILL))

import forge_ingest  # noqa: E402


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(
            "Usage: python scripts/codegen/run_sigil_forge_ingest.py "
            "\"<intent>\" [--output file.json]"
        )
        return 1
    intent = sys.argv[1]
    output = None
    if "--output" in sys.argv:
        i = sys.argv.index("--output")
        if i + 1 < len(sys.argv):
            output = sys.argv[i + 1]
    env = forge_ingest.from_intent(intent, request_id="cli")
    text = json.dumps(env, indent=2, sort_keys=True)
    if output:
        Path(output).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
