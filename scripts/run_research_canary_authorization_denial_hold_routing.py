from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.research_canary_authorization_denial_hold_routing import (  # noqa: E402
    build_research_canary_authorization_denial_hold_routing,
    write_research_canary_authorization_denial_hold_routing,
)
from scripts.common.runner import print_packet_fields, run_packet_and_write  # noqa: E402

OUT_PATH = Path("out/research_canary_authorization_denial_hold_routing/latest.json")
P116_DEFAULT_PATH = Path("out/research_canary_authorization_decision_record/latest.json")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build P117 research canary authorization denial/hold routing."
    )
    parser.add_argument(
        "--p116-path",
        default=str(P116_DEFAULT_PATH),
        help=(
            "Path to upstream P116 research_canary_authorization_decision_record packet "
            "(default: %(default)s)."
        ),
    )
    parser.add_argument(
        "--routing-observations-path",
        default=None,
        help=(
            "Optional path to per-candidate routing observations for candidates "
            "included in P116 decision output."
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
    p116_packet: dict[str, Any] | None = None,
    routing_observations_packet: dict[str, Any] | None = None,
    repo_root: str | Path = ROOT,
    out_path: str | Path | None = None,
) -> dict[str, object]:
    return run_packet_and_write(
        repo_root=repo_root,
        out_path=out_path,
        relative_out_path=OUT_PATH,
        build_packet=lambda **_: build_research_canary_authorization_denial_hold_routing(
            p116_packet=p116_packet,
            routing_observations_packet=routing_observations_packet,
        ),
        write_packet=write_research_canary_authorization_denial_hold_routing,
    )


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    p116_packet = _load_json_packet(args.p116_path)
    routing_observations_packet = _load_json_packet(args.routing_observations_path)
    packet = run(
        p116_packet=p116_packet,
        routing_observations_packet=routing_observations_packet,
    )
    print_packet_fields(packet, "status", "lane_status", "recommended_next_lane")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
