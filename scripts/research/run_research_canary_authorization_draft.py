from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.research_canary_authorization_draft import (  # noqa: E402
    build_research_canary_authorization_draft,
    write_research_canary_authorization_draft,
)
from scripts.common.runner import print_packet_fields, run_packet_and_write  # noqa: E402

OUT_PATH = Path("out/research_canary_authorization_draft/latest.json")
P110_DEFAULT_PATH = Path("out/research_canary_plan_review_record/latest.json")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build P111 research canary authorization draft."
    )
    parser.add_argument(
        "--p110-path",
        default=str(P110_DEFAULT_PATH),
        help=(
            "Path to upstream P110 research_canary_plan_review_record packet "
            "(default: %(default)s)."
        ),
    )
    parser.add_argument(
        "--authorization-draft-observations-path",
        default=None,
        help=(
            "Optional path to per-candidate authorization draft observations for "
            "P110 plan-review-complete candidates."
        ),
    )
    return parser.parse_args(argv)


def _load_json_packet(path: str | Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    packet_path = Path(path)
    if not packet_path.exists():
        return None
    try:
        data = json.loads(packet_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if not isinstance(data, dict):
        return None
    return data


def run(
    *,
    p110_packet: dict[str, Any] | None = None,
    authorization_draft_observations_packet: dict[str, Any] | None = None,
    repo_root: str | Path = ROOT,
    out_path: str | Path | None = None,
) -> dict[str, object]:
    return run_packet_and_write(
        repo_root=repo_root,
        out_path=out_path,
        relative_out_path=OUT_PATH,
        build_packet=lambda **_: build_research_canary_authorization_draft(
            p110_packet=p110_packet,
            authorization_draft_observations_packet=authorization_draft_observations_packet,
        ),
        write_packet=write_research_canary_authorization_draft,
    )


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    p110_packet = _load_json_packet(args.p110_path)
    authorization_draft_observations_packet = _load_json_packet(
        args.authorization_draft_observations_path
    )
    packet = run(
        p110_packet=p110_packet,
        authorization_draft_observations_packet=authorization_draft_observations_packet,
    )
    print_packet_fields(
        packet,
        "status",
        "canary_authorization_draft_status",
        "recommended_next_lane",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
