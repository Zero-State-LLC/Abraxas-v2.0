from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.temporal_continuity_operator_authorization_record_approval_record_seal_finalization_decision import (  # noqa: E402
    DEFAULT_HUMAN_DECISION_PATH,
    build_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_decision,
    write_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_decision,
)

OUT_PATH = Path(
    "out/temporal_continuity_operator_authorization_record_approval_record_seal_finalization_decision/latest.json"
)


def _load_json_dict(path: str | Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else None
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None


def run(
    *,
    repo_root: str | Path = ROOT,
    human_decision_path: str | Path | None = None,
    out_path: str | Path | None = None,
) -> dict[str, object]:
    resolved_decision_path = (
        human_decision_path
        if human_decision_path is not None
        else Path(repo_root) / DEFAULT_HUMAN_DECISION_PATH
    )
    human_decision_packet = _load_json_dict(resolved_decision_path)
    artifact_path_str = (
        str(resolved_decision_path) if human_decision_packet is not None else None
    )

    packet = build_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_decision(
        repo_root=repo_root,
        human_decision_packet=human_decision_packet,
        human_decision_artifact_path=artifact_path_str,
    )
    target = Path(out_path) if out_path is not None else Path(repo_root) / OUT_PATH
    write_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_decision(
        target, packet
    )
    return packet


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--human-decision-path",
        default=None,
        help=(
            "Path to human decision artifact JSON. "
            f"If omitted, checks the default location: {DEFAULT_HUMAN_DECISION_PATH}"
        ),
    )
    args = parser.parse_args(argv)
    packet = run(human_decision_path=args.human_decision_path)
    print(packet["approval_record_seal_finalization_decision_status"])
    print(packet["recommended_next_lane"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
