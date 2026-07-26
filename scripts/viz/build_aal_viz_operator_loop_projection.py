#!/usr/bin/env python3
"""Build a read-only AAL-Viz operator-loop projection.

Reads optional WorkPacket.v1 / HandoffEnvelope.v1 JSON files from:
  out/operator_loop/work_packets/*.json
  out/operator_loop/handoffs/*.json

When no sources exist, emits a dry-run projection from example packets so the
console/adapters can still load a well-formed, authority-locked document.

Writes:
  out/projections/aal_viz_operator_loop.v1.latest.json
  apps/aal-viz-live-console/public/operator-loop-projection.json (if console present)

Authority: projection_only. No assignment, approval, merge, or deploy capability.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.operator_loop import (
    build_operator_loop_projection,
    collect_local_truth_surfaces,
    example_handoff,
    example_work_packet,
)

DEFAULT_PACKET_DIR = ROOT / "out" / "operator_loop" / "work_packets"
DEFAULT_HANDOFF_DIR = ROOT / "out" / "operator_loop" / "handoffs"
DEFAULT_EVIDENCE_DIR = ROOT / "out" / "operator_loop" / "evidence"
DEFAULT_OUT = ROOT / "out" / "projections" / "aal_viz_operator_loop.v1.latest.json"
CONSOLE_OUT = (
    ROOT
    / "apps"
    / "aal-viz-live-console"
    / "public"
    / "operator-loop-projection.json"
)


def _load_json_dir(directory: Path) -> list[dict[str, Any]]:
    if not directory.is_dir():
        return []
    items: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"warn: skip {path}: {exc}", file=sys.stderr)
            continue
        if isinstance(payload, dict):
            items.append(payload)
        elif isinstance(payload, list):
            items.extend(p for p in payload if isinstance(p, dict))
    return items


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build read-only AAL-Viz operator-loop projection"
    )
    parser.add_argument(
        "--packet-dir",
        type=Path,
        default=DEFAULT_PACKET_DIR,
        help="Directory of WorkPacket.v1 JSON files",
    )
    parser.add_argument(
        "--handoff-dir",
        type=Path,
        default=DEFAULT_HANDOFF_DIR,
        help="Directory of HandoffEnvelope.v1 JSON files",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUT,
        help="Projection output path",
    )
    parser.add_argument(
        "--no-console-copy",
        action="store_true",
        help="Do not write apps/aal-viz-live-console/public/operator-loop-projection.json",
    )
    parser.add_argument(
        "--dry-run-examples",
        action="store_true",
        help="Force example packets even if source dirs have files",
    )
    parser.add_argument(
        "--evidence-dir",
        type=Path,
        default=DEFAULT_EVIDENCE_DIR,
        help="Directory of github.v1.json / notion.v1.json / ci.v1.json evidence files",
    )
    parser.add_argument(
        "--no-local-git",
        action="store_true",
        help="Do not read local .git refs for GitHub tip evidence",
    )
    args = parser.parse_args(argv)

    packets = [] if args.dry_run_examples else _load_json_dir(args.packet_dir)
    handoffs = [] if args.dry_run_examples else _load_json_dir(args.handoff_dir)
    source_paths: list[str] = []

    if not packets and not handoffs:
        packets = [
            example_work_packet(
                work_packet_id="WP-dry-run-grok",
                producer_system="GROK",
                files=["design-system/aal-viz/operator_loop/README.md"],
            ),
            example_work_packet(
                work_packet_id="WP-dry-run-codex",
                producer_system="CODEX",
                files=[
                    "contracts/engineering/work_packet.v1.schema.json",
                    "core/operator_loop.py",
                ],
            ),
        ]
        handoffs = [example_handoff(work_packet_id="WP-dry-run-codex")]
        source_paths = ["dry-run:example_work_packet", "dry-run:example_handoff"]
    else:
        if args.packet_dir.is_dir():
            source_paths.append(str(args.packet_dir.relative_to(ROOT)))
        if args.handoff_dir.is_dir():
            source_paths.append(str(args.handoff_dir.relative_to(ROOT)))

    truth_surfaces = collect_local_truth_surfaces(
        repo_root=ROOT,
        evidence_dir=args.evidence_dir,
        include_local_git=not args.no_local_git,
    )
    if args.evidence_dir.is_dir():
        try:
            source_paths.append(str(args.evidence_dir.relative_to(ROOT)))
        except ValueError:
            source_paths.append(str(args.evidence_dir))

    projection = build_operator_loop_projection(
        work_packets=packets,
        handoffs=handoffs,
        source_paths=source_paths,
        truth_surfaces=truth_surfaces,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(projection, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {args.output.relative_to(ROOT)}")
    print(
        "summary:",
        json.dumps(projection["summary"], sort_keys=True),
    )
    print("authority:", json.dumps(projection["authority"], sort_keys=True))

    if not args.no_console_copy and CONSOLE_OUT.parent.is_dir():
        CONSOLE_OUT.write_text(
            json.dumps(projection, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"wrote {CONSOLE_OUT.relative_to(ROOT)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
