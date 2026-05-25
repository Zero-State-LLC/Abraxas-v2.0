from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.research_stabilization_window_monitor import (  # noqa: E402
    build_research_stabilization_window_monitor,
    write_research_stabilization_window_monitor,
)
from scripts.common.runner import print_packet_fields, run_packet_and_write  # noqa: E402

OUT_PATH = Path("out/research_stabilization_window_monitor/latest.json")
P101_DEFAULT_PATH = Path("out/research_shadow_stabilization_receipt/latest.json")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build P102 research stabilization window monitor packet."
    )
    parser.add_argument(
        "--p101-path",
        default=str(P101_DEFAULT_PATH),
        help=(
            "Path to upstream P101 research_shadow_stabilization_receipt packet "
            "(default: %(default)s)."
        ),
    )
    parser.add_argument(
        "--observations-path",
        default=None,
        help=(
            "Optional path to candidate observations containing observed cycles and "
            "proof flags."
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
    p101_packet: dict[str, Any] | None = None,
    observations_packet: dict[str, Any] | None = None,
    repo_root: str | Path = ROOT,
    out_path: str | Path | None = None,
) -> dict[str, object]:
    return run_packet_and_write(
        repo_root=repo_root,
        out_path=out_path,
        relative_out_path=OUT_PATH,
        build_packet=lambda **_: build_research_stabilization_window_monitor(
            p101_packet=p101_packet,
            observations_packet=observations_packet,
        ),
        write_packet=write_research_stabilization_window_monitor,
    )


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    p101_packet = _load_json_packet(args.p101_path)
    observations_packet = _load_json_packet(args.observations_path)
    packet = run(p101_packet=p101_packet, observations_packet=observations_packet)
    print_packet_fields(
        packet,
        "status",
        "stabilization_window_monitor_status",
        "recommended_next_lane",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
