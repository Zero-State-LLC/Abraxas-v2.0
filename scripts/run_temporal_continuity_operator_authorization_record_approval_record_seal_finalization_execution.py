from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.temporal_continuity_operator_authorization_record_approval_record_seal_finalization_execution import (  # noqa: E402
    build_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_execution,
    write_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_execution,
)

OUT_PATH = Path(
    "out/temporal_continuity_operator_authorization_record_approval_record_seal_finalization_execution/latest.json"
)


def run(
    *,
    repo_root: str | Path = ROOT,
    out_path: str | Path | None = None,
) -> dict[str, object]:
    packet = build_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_execution(
        repo_root=repo_root,
    )
    target = Path(out_path) if out_path is not None else Path(repo_root) / OUT_PATH
    write_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_execution(
        target, packet
    )
    return packet


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.parse_args()
    packet = run()
    print(packet["finalization_execution_status"])
    print(packet["recommended_next_lane"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
