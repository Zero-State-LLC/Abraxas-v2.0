from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.research_controlled_canary_envelope_draft import (  # noqa: E402
    build_research_controlled_canary_envelope_draft,
    write_research_controlled_canary_envelope_draft,
)
from scripts.common.runner import print_packet_fields, run_packet_and_write  # noqa: E402

OUT_PATH = Path("out/research_controlled_canary_envelope_draft/latest.json")
P117_DEFAULT_PATH = Path("out/research_canary_authorization_denial_hold_routing/latest.json")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build P118 research controlled canary envelope draft."
    )
    parser.add_argument(
        "--p117-path",
        default=str(P117_DEFAULT_PATH),
        help=(
            "Path to upstream P117 research_canary_authorization_denial_hold_routing "
            "packet (default: %(default)s)."
        ),
    )
    parser.add_argument(
        "--envelope-observations-path",
        default=None,
        help=(
            "Optional path to per-candidate envelope draft observations for candidates "
            "approved for controlled envelope planning in P117."
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
    p117_packet: dict[str, Any] | None = None,
    envelope_observations_packet: dict[str, Any] | None = None,
    repo_root: str | Path = ROOT,
    out_path: str | Path | None = None,
) -> dict[str, object]:
    return run_packet_and_write(
        repo_root=repo_root,
        out_path=out_path,
        relative_out_path=OUT_PATH,
        build_packet=lambda **_: build_research_controlled_canary_envelope_draft(
            p117_packet=p117_packet,
            envelope_observations_packet=envelope_observations_packet,
        ),
        write_packet=write_research_controlled_canary_envelope_draft,
    )


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    p117_packet = _load_json_packet(args.p117_path)
    envelope_observations_packet = _load_json_packet(args.envelope_observations_path)
    packet = run(
        p117_packet=p117_packet,
        envelope_observations_packet=envelope_observations_packet,
    )
    print_packet_fields(packet, "status", "lane_status", "recommended_next_lane")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
