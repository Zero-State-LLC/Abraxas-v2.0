from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.research_operator_stabilization_decision_record import (  # noqa: E402
    build_research_operator_stabilization_decision_record,
    write_research_operator_stabilization_decision_record,
)
from scripts.common.runner import print_packet_fields, run_packet_and_write  # noqa: E402

OUT_PATH = Path("out/research_operator_stabilization_decision_record/latest.json")
P99_DEFAULT_PATH = Path("out/research_cross_drop_conflict_scan/latest.json")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build P100 research operator stabilization decision record packet."
    )
    parser.add_argument(
        "--p99-path",
        default=str(P99_DEFAULT_PATH),
        help=(
            "Path to the upstream P99 research_cross_drop_conflict_scan packet "
            "(default: %(default)s)."
        ),
    )
    return parser.parse_args(argv)


def _load_p99_packet(path: str | Path) -> dict[str, object] | None:
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
    p99_packet: dict[str, object] | None = None,
    repo_root: str | Path = ROOT,
    out_path: str | Path | None = None,
) -> dict[str, object]:
    return run_packet_and_write(
        repo_root=repo_root,
        out_path=out_path,
        relative_out_path=OUT_PATH,
        build_packet=lambda **_: build_research_operator_stabilization_decision_record(
            p99_packet=p99_packet
        ),
        write_packet=write_research_operator_stabilization_decision_record,
    )


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    p99_packet = _load_p99_packet(args.p99_path)
    packet = run(p99_packet=p99_packet)
    print_packet_fields(
        packet,
        "status",
        "operator_decision_record_status",
        "recommended_next_lane",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
