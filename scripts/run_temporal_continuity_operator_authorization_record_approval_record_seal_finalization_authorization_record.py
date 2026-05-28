from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.temporal_continuity_operator_authorization_record_approval_record_seal_finalization_authorization_record import (  # noqa: E402
    build_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_authorization_record,
    write_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_authorization_record,
)

OUT_PATH = Path(
    "out/temporal_continuity_operator_authorization_record_approval_record_seal_finalization_authorization_record/latest.json"
)


def _load_json_dict(path: str) -> dict | None:
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def run(
    *,
    repo_root: str | Path = ROOT,
    out_path: str | Path | None = None,
    human_authorization_path: str | None = None,
) -> dict[str, object]:
    human_packet = None
    if human_authorization_path is not None:
        human_packet = _load_json_dict(human_authorization_path)

    packet = build_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_authorization_record(
        repo_root=repo_root,
        human_authorization_artifact_path=human_authorization_path,
        human_authorization_packet=human_packet,
    )
    target = Path(out_path) if out_path is not None else Path(repo_root) / OUT_PATH
    write_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_authorization_record(
        target, packet
    )
    return packet


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--human-authorization-path", default=None)
    args = parser.parse_args()
    packet = run(human_authorization_path=args.human_authorization_path)
    print(packet["finalization_authorization_record_status"])
    print(packet["recommended_next_lane"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
