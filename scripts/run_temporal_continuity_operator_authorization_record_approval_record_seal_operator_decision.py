from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.temporal_continuity_operator_authorization_record_approval_record_seal_operator_decision import (  # noqa: E402
    DEFAULT_HUMAN_DECISION_PATH,
    build_temporal_continuity_operator_authorization_record_approval_record_seal_operator_decision,
    write_temporal_continuity_operator_authorization_record_approval_record_seal_operator_decision,
)

OUT_PATH = Path(
    "out/temporal_continuity_operator_authorization_record_approval_record_seal_operator_decision/latest.json"
)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build P96 temporal continuity operator authorization record "
            "approval record seal operator decision packet."
        )
    )
    parser.add_argument(
        "--human-decision-path",
        default=None,
        help=(
            "Optional path to the operator human decision artifact. "
            f"If omitted, checks the default location: {DEFAULT_HUMAN_DECISION_PATH}"
        ),
    )
    return parser.parse_args(argv)


def _load_json_dict(path: str | Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    p = Path(path)
    if not p.exists():
        return None
    try:
        payload = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return payload if isinstance(payload, dict) else None


def run(
    *,
    repo_root: str | Path = ROOT,
    human_decision_path: str | None = None,
    out_path: str | Path | None = None,
) -> dict[str, object]:
    resolved_decision_path: str | None = human_decision_path
    if resolved_decision_path is None:
        default = Path(repo_root) / DEFAULT_HUMAN_DECISION_PATH
        if default.exists():
            resolved_decision_path = str(default)

    human_decision_packet = _load_json_dict(resolved_decision_path)

    packet = build_temporal_continuity_operator_authorization_record_approval_record_seal_operator_decision(
        repo_root=repo_root,
        human_decision_packet=human_decision_packet,
        human_decision_artifact_path=resolved_decision_path,
    )
    target = Path(out_path) if out_path is not None else Path(repo_root) / OUT_PATH
    write_temporal_continuity_operator_authorization_record_approval_record_seal_operator_decision(
        target, packet
    )
    return packet


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    packet = run(human_decision_path=args.human_decision_path)
    print(packet["approval_record_seal_operator_decision_status"])
    print(packet["recommended_next_lane"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
