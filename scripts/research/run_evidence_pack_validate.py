#!/usr/bin/env python3
"""Validate EvidencePack.v0 JSON against contracts + semantic rules.

Uses core.signal.evidence_pack (canonical AI OS syscall validator).

Examples:
  python scripts/research/run_evidence_pack_validate.py \\
    skills/abx-familiar-signal-forager/fixtures/evidence_pack_hermes_skill_os_2026-07-27.v0.json

  python scripts/research/run_evidence_pack_validate.py --emit-report PATH
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.signal.evidence_pack import validate_path  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="Path to EvidencePack.v0 JSON")
    parser.add_argument(
        "--emit-report",
        action="store_true",
        help="Print full JSON report (default: short human summary)",
    )
    args = parser.parse_args(argv)

    report = validate_path(args.path, repo_root=ROOT)
    if args.emit_report:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        if report["ok"]:
            print(f"VALID {report['path']}")
            print(
                json.dumps(
                    {
                        "pack_id": report.get("pack_id"),
                        "topic": report.get("topic"),
                        "register_counts": report.get("register_counts"),
                        "source_count": report.get("source_count"),
                        "commercial_claims_blocked": report.get(
                            "commercial_claims_blocked"
                        ),
                        "evidence_density": report.get("evidence_density"),
                    },
                    indent=2,
                )
            )
        else:
            print(f"INVALID {report['path']}", file=sys.stderr)
            for err in report.get("errors") or []:
                print(f"  - {err}", file=sys.stderr)

    return 0 if report["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
