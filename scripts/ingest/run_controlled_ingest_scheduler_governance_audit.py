#!/usr/bin/env python3
"""WP-D4-C2 sole-writer: controlled ingest scheduler governance audit packet."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import infer_out_root, write_classified_json
from core.ingest.controlled_ingest_scheduler_governance_audit import (
    build_controlled_ingest_scheduler_governance_audit_packet,
    render_controlled_ingest_scheduler_governance_audit_markdown,
)

DEFAULT_OUT = Path(
    "out/audit/controlled_ingest_scheduler_governance_audit_001.latest.json"
)


def run(*, out_json: Path, repo_root: Path | None = None) -> dict:
    root = repo_root or REPO_ROOT
    packet = build_controlled_ingest_scheduler_governance_audit_packet(repo_root=root)
    out_json = Path(out_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    write_classified_json(
        out_json,
        packet,
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=infer_out_root(out_json, fallback=root / "out"),
    )
    out_json.with_suffix(".md").write_text(
        render_controlled_ingest_scheduler_governance_audit_markdown(packet),
        encoding="utf-8",
    )
    return packet


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)
    packet = run(out_json=args.out)
    print(
        json.dumps(
            {
                "final_status": packet.get("final_status"),
                "recommended_next_step": packet.get("recommended_next_step"),
                "output": str(args.out),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if packet.get("final_status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
