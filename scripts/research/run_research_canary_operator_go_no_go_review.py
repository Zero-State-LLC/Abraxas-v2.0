from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.research_canary_operator_go_no_go_review import (  # noqa: E402
    build_research_canary_operator_go_no_go_review,
    write_research_canary_operator_go_no_go_review,
)
from scripts.common.runner import print_packet_fields, run_packet_and_write  # noqa: E402

OUT_PATH = Path("out/research_canary_operator_go_no_go_review/latest.json")
P120_DEFAULT_PATH = Path("out/research_canary_rollback_termination_governance/latest.json")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build P121 research canary operator go/no-go review."
    )
    parser.add_argument(
        "--p120-path",
        default=str(P120_DEFAULT_PATH),
        help=(
            "Path to upstream P120 research_canary_rollback_termination_governance packet "
            "(default: %(default)s)."
        ),
    )
    parser.add_argument(
        "--go-no-go-observations-path",
        default=None,
        help=(
            "Optional path to per-candidate go/no-go observations for P120 "
            "rollback-termination-governance-complete candidates."
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
    p120_packet: dict[str, Any] | None = None,
    go_no_go_observations_packet: dict[str, Any] | None = None,
    repo_root: str | Path = ROOT,
    out_path: str | Path | None = None,
) -> dict[str, object]:
    return run_packet_and_write(
        repo_root=repo_root,
        out_path=out_path,
        relative_out_path=OUT_PATH,
        build_packet=lambda **_: build_research_canary_operator_go_no_go_review(
            p120_packet=p120_packet,
            go_no_go_observations_packet=go_no_go_observations_packet,
        ),
        write_packet=write_research_canary_operator_go_no_go_review,
    )


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    p120_packet = _load_json_packet(args.p120_path)
    go_no_go_observations_packet = _load_json_packet(args.go_no_go_observations_path)
    packet = run(
        p120_packet=p120_packet,
        go_no_go_observations_packet=go_no_go_observations_packet,
    )
    print_packet_fields(packet, "status", "lane_status", "recommended_next_lane")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
