from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.research_boundary_decay_analysis import (  # noqa: E402
    build_research_boundary_decay_analysis,
    write_research_boundary_decay_analysis,
)
from scripts.common.runner import print_packet_fields, run_packet_and_write  # noqa: E402

OUT_PATH = Path("out/research_boundary_decay_analysis/latest.json")
P103_DEFAULT_PATH = Path("out/research_shadow_replay_audit/latest.json")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build P104 research boundary decay analysis packet."
    )
    parser.add_argument(
        "--p103-path",
        default=str(P103_DEFAULT_PATH),
        help=(
            "Path to upstream P103 research_shadow_replay_audit packet "
            "(default: %(default)s)."
        ),
    )
    parser.add_argument(
        "--boundary-observations-path",
        default=None,
        help=(
            "Optional path to per-candidate boundary observations for replay-pass "
            "candidates."
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
    p103_packet: dict[str, Any] | None = None,
    boundary_observations_packet: dict[str, Any] | None = None,
    repo_root: str | Path = ROOT,
    out_path: str | Path | None = None,
) -> dict[str, object]:
    return run_packet_and_write(
        repo_root=repo_root,
        out_path=out_path,
        relative_out_path=OUT_PATH,
        build_packet=lambda **_: build_research_boundary_decay_analysis(
            p103_packet=p103_packet,
            boundary_observations_packet=boundary_observations_packet,
        ),
        write_packet=write_research_boundary_decay_analysis,
    )


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    p103_packet = _load_json_packet(args.p103_path)
    boundary_observations_packet = _load_json_packet(args.boundary_observations_path)
    packet = run(
        p103_packet=p103_packet,
        boundary_observations_packet=boundary_observations_packet,
    )
    print_packet_fields(
        packet,
        "status",
        "boundary_decay_analysis_status",
        "recommended_next_lane",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
