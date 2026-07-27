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
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / "out" / "signal_forage"


def _utc_slug(topic: str) -> str:
    day = datetime.now(UTC).strftime("%Y-%m-%d")
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
    """Delegate to canonical core.signal.evidence_pack validator."""
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from core.signal.evidence_pack import validate_path

    report = validate_path(path, repo_root=ROOT)
    if report["ok"]:
        print(f"VALID {report['path']}")
        print(
            json.dumps(
                {
                    "pack_id": report.get("pack_id"),
                    "topic": report.get("topic"),
                    "register_counts": report.get("register_counts"),
                    "source_count": report.get("source_count"),
                    "commercial_claims_blocked": report.get("commercial_claims_blocked"),
                    "evidence_density": report.get("evidence_density"),
                },
                indent=2,
            )
        )
        return 0
    print(f"INVALID {report['path']}", file=sys.stderr)
    for err in report.get("errors") or []:
        print(f"  - {err}", file=sys.stderr)
    return 2


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
