from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.research_promotion_blocker_ledger import (  # noqa: E402
    build_research_promotion_blocker_ledger,
    write_research_promotion_blocker_ledger,
)
from scripts.common.runner import print_packet_fields, run_packet_and_write  # noqa: E402

OUT_PATH = Path("out/research_promotion_blocker_ledger/latest.json")
P104_DEFAULT_PATH = Path("out/research_boundary_decay_analysis/latest.json")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build P105 research promotion blocker ledger packet."
    )
    parser.add_argument(
        "--p104-path",
        default=str(P104_DEFAULT_PATH),
        help=(
            "Path to upstream P104 research_boundary_decay_analysis packet "
            "(default: %(default)s)."
        ),
    )
    parser.add_argument(
        "--blocker-observations-path",
        default=None,
        help=(
            "Optional path to per-candidate promotion blocker observations for "
            "boundary-stable candidates."
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
    p104_packet: dict[str, Any] | None = None,
    blocker_observations_packet: dict[str, Any] | None = None,
    repo_root: str | Path = ROOT,
    out_path: str | Path | None = None,
) -> dict[str, object]:
    return run_packet_and_write(
        repo_root=repo_root,
        out_path=out_path,
        relative_out_path=OUT_PATH,
        build_packet=lambda **_: build_research_promotion_blocker_ledger(
            p104_packet=p104_packet,
            blocker_observations_packet=blocker_observations_packet,
        ),
        write_packet=write_research_promotion_blocker_ledger,
    )


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    p104_packet = _load_json_packet(args.p104_path)
    blocker_observations_packet = _load_json_packet(args.blocker_observations_path)
    packet = run(
        p104_packet=p104_packet,
        blocker_observations_packet=blocker_observations_packet,
    )
    print_packet_fields(
        packet,
        "status",
        "promotion_blocker_ledger_status",
        "recommended_next_lane",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
