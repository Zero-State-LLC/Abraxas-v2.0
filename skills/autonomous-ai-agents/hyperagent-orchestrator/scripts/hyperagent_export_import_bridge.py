#!/usr/bin/env python3
"""Map Abraxas payloads to HyperAgent role/skill JSON and back.

This bridge is intentionally conservative and schema-light so the mapping can
be reviewed before any live HyperAgent API interaction.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def stable_dump(obj: Any) -> str:
    return json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False)


def abraxas_to_hyperagent(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": payload.get("name", "abx-bridge-role"),
        "version": payload.get("version", "0.1.0"),
        "mission": payload.get("summary") or payload.get("mission") or "Bridge Abraxas output into a HyperAgent role.",
        "trigger": payload.get("trigger", {"type": "manual"}),
        "tools": payload.get("tools", ["web_search"]),
        "budget": payload.get("budget", {"max_cost_usd": 1.0, "max_steps": 8}),
        "observed": payload.get("observed"),
        "inferred": payload.get("inferred"),
        "speculative": payload.get("speculative"),
        "provenance": payload.get("provenance", {}),
        "source_uri": payload.get("source_uri"),
        "canonical_hash": payload.get("canonical_hash"),
    }


def hyperagent_to_abraxas(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "observed": payload,
        "inferred": {
            "role": payload.get("name"),
            "version": payload.get("version"),
            "tool_count": len(payload.get("tools", [])),
        },
        "speculative": {
            "next_step": "Review role policy and deploy only after validation"
        },
        "provenance": {
            "source": "hyperagent-export",
            "canonical_hash": payload.get("canonical_hash"),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["export", "import"], required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", help="Optional output file path")
    args = parser.parse_args()

    payload = load_json(args.input)
    mapped = abraxas_to_hyperagent(payload) if args.mode == "export" else hyperagent_to_abraxas(payload)
    text = stable_dump(mapped)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
