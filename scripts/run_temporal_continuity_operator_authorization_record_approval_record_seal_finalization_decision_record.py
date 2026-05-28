from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.temporal_continuity_operator_authorization_record_approval_record_seal_finalization_decision_record import (  # noqa: E402
    build_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_decision_record,
    write_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_decision_record,
)

OUT_PATH = Path(
    "out/temporal_continuity_operator_authorization_record_approval_record_seal_finalization_decision_record/latest.json"
)


def run(
    *,
    repo_root: str | Path = ROOT,
    out_path: str | Path | None = None,
) -> dict:
    packet = build_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_decision_record(
        repo_root=repo_root,
    )
    target = Path(out_path) if out_path is not None else Path(repo_root) / OUT_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    write_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_decision_record(
        target, packet
    )
    return packet


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo-root",
        default=str(ROOT),
        help="Path to repository root. Defaults to the parent of the scripts/ directory.",
    )
    args = parser.parse_args(argv)
    packet = run(repo_root=args.repo_root)
    print(packet["finalization_decision_record_status"])
    print(packet["recommended_next_lane"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
