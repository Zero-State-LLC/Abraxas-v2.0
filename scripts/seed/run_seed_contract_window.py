#!/usr/bin/env python3
"""Emit SeedContractWindow.v0 JSON. SHADOW only. No Seed Corpus write. No network."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

SCHEMA_VERSION = "SeedContractWindow.v0"
DEFAULT_KEYS = ("aura_farming", "HYPER.STITIO", "AI_SLOP")
AUTHORITY = {
    "execution_authority": False,
    "promotion_authorized": False,
    "forecast_routing_authorized": False,
    "canon_mutation_allowed": False,
}


def build_window(date_pt: str, rows: list[dict]) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "lane": "SHADOW",
        "advisory_only": True,
        "date_pt": date_pt,
        "window": {
            "tz": "America/Los_Angeles",
            "start": date_pt,
            "end": date_pt,
        },
        "unit": "unique_grounded_post_ids_or_urls",
        "sample_capped": True,
        "rows": rows,
        "velocity": "NOT_COMPUTABLE",
        "exclusions": [
            "companion 03 prose",
            "press views as slang velocity",
            "SUAS",
            "$BRAINROT ticker",
            "generated mutations",
            "vibe coding merged into AI_SLOP",
        ],
        "authority": AUTHORITY,
    }


def rows_from_counts(counts: dict[str, list[str]]) -> list[dict]:
    out = []
    for key in DEFAULT_KEYS:
        ids = list(dict.fromkeys(counts.get(key, [])))
        out.append(
            {
                "construct_id": key,
                "count_or_nc": len(ids) if ids else "NOT_COMPUTABLE",
                "source_ids": ids,
                "register": "OBSERVED" if ids else "NOT_COMPUTABLE",
            }
        )
    return out


def main() -> int:
    p = argparse.ArgumentParser(description="Emit SeedContractWindow.v0 (SHADOW)")
    p.add_argument("--date-pt", default=date.today().isoformat())
    p.add_argument(
        "--counts-json",
        type=Path,
        help="JSON object construct_id -> list of source IDs",
    )
    p.add_argument("--out", type=Path, default=None)
    args = p.parse_args()

    counts: dict[str, list[str]] = {}
    if args.counts_json:
        counts = json.loads(args.counts_json.read_text(encoding="utf-8"))
    rows = rows_from_counts(counts)
    window = build_window(args.date_pt, rows)

    out = args.out
    if out is None:
        out = Path("out/signal_forage") / args.date_pt / "seed_contract_window.v0.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(window, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print(str(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
