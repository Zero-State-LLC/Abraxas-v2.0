#!/usr/bin/env python3
"""SHADOW signal forage template runner (cron / operator).

Does NOT live-scrape by default. Modes:
  --emit-stub     write a NOT_COMPUTABLE placeholder pack (no network)
  --validate PATH validate an existing EvidencePack.v0 JSON

Live forage is performed by Hermes with abx-familiar-signal-forager
(web tools + register tags). This script is the durable hand-off + gate.

Authority: execution_authority=false always.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / "out" / "signal_forage"


def _utc_slug(topic: str) -> str:
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in topic.lower())[:48].strip("-")
    return f"{day}_{safe or 'topic'}"


def emit_stub(topic: str, intent: str, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    pack = {
        "schema_version": "EvidencePack.v0",
        "pack_id": f"ep_stub_{_utc_slug(topic).replace('-', '')[:24]}",
        "topic": topic,
        "intent": intent,
        "time_horizon": "stub",
        "must_answer": [f"What OBSERVED evidence exists for: {topic}?"],
        "hard_exclusions": ["No network in stub mode"],
        "sources": [],
        "claims": [
            {
                "claim_id": "C001",
                "text": "Stub pack only — run Hermes abx-familiar-signal-forager for live sources.",
                "register": "NOT_COMPUTABLE",
                "supports_questions": [0],
                "source_ids": [],
                "join_logic": None,
                "confidence_note": "cron stub",
            }
        ],
        "answers": [
            {
                "question_index": 0,
                "status": "NOT_COMPUTABLE",
                "summary": "Stub — no live forage executed",
                "claim_ids": ["C001"],
            }
        ],
        "authority": {
            "execution_authority": False,
            "promotion_authorized": False,
            "forecast_routing_authorized": False,
            "canon_mutation_allowed": False,
            "lane": "SHADOW",
        },
        "provenance": {
            "producer_system": "HERMES",
            "skill_id": "abx-familiar-signal-forager",
            "tool_trace_summary": "scripts/research/run_shadow_signal_forage_template.py --emit-stub",
            "repo_root": str(ROOT),
            "notes": "cron template stub",
        },
        "observed_source_count": 0,
        "register_counts": {
            "OBSERVED": 0,
            "INFERRED": 0,
            "SPECULATIVE": 0,
            "NOT_COMPUTABLE": 1,
        },
    }
    path = out_dir / "evidence_pack.v0.json"
    path.write_text(json.dumps(pack, indent=2) + "\n", encoding="utf-8")
    brief = out_dir / "evidence_brief.md"
    brief.write_text(
        f"# Stub forage brief\n\nTopic: {topic}\n\n"
        "No live sources. Invoke Hermes with skill `abx-familiar-signal-forager`.\n",
        encoding="utf-8",
    )
    return path


def validate_pack(path: Path) -> int:
    data = json.loads(path.read_text(encoding="utf-8"))
    required = [
        "schema_version",
        "pack_id",
        "topic",
        "intent",
        "must_answer",
        "sources",
        "claims",
        "authority",
        "provenance",
    ]
    missing = [k for k in required if k not in data]
    if missing:
        print(f"INVALID missing keys: {missing}", file=sys.stderr)
        return 2
    if data.get("schema_version") != "EvidencePack.v0":
        print("INVALID schema_version", file=sys.stderr)
        return 2
    auth = data.get("authority") or {}
    if auth.get("execution_authority") is not False:
        print("INVALID execution_authority must be false", file=sys.stderr)
        return 2
    for claim in data.get("claims") or []:
        reg = claim.get("register")
        if reg == "OBSERVED" and not claim.get("source_ids"):
            print(f"INVALID OBSERVED claim without sources: {claim.get('claim_id')}", file=sys.stderr)
            return 2
        if reg == "INFERRED" and (not claim.get("join_logic") or len(claim.get("source_ids") or []) < 2):
            print(f"INVALID INFERRED claim: {claim.get('claim_id')}", file=sys.stderr)
            return 2
    print(f"VALID {path}")
    print(json.dumps({
        "pack_id": data.get("pack_id"),
        "topic": data.get("topic"),
        "register_counts": data.get("register_counts"),
        "source_count": len(data.get("sources") or []),
    }, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic", default="operator-topic", help="Forage topic slug/label")
    parser.add_argument(
        "--intent",
        default="tech",
        choices=["research", "competitive", "market", "regulatory", "tech", "memetic", "local_ops", "other"],
    )
    parser.add_argument("--out", type=Path, default=None, help="Output directory")
    parser.add_argument("--emit-stub", action="store_true", help="Write NOT_COMPUTABLE stub pack")
    parser.add_argument("--validate", type=Path, default=None, help="Validate EvidencePack.v0 JSON")
    args = parser.parse_args(argv)

    if args.validate:
        return validate_pack(args.validate)

    if args.emit_stub:
        out_dir = args.out or (DEFAULT_OUT / _utc_slug(args.topic))
        path = emit_stub(args.topic, args.intent, out_dir)
        print(path)
        return validate_pack(path)

    print(
        "No action. Use --emit-stub for placeholder or --validate PATH.\n"
        "Live forage: Hermes skill abx-familiar-signal-forager "
        "(then pass evidence_pack_path to Neon Genie).",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
