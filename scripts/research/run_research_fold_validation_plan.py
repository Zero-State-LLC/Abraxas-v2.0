from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.research_fold_validation_plan import (  # noqa: E402
    build_research_fold_validation_plan,
    write_research_fold_validation_plan,
)
from scripts.common.runner import print_packet_fields, run_packet_and_write  # noqa: E402

OUT_PATH = Path("out/research_fold_validation_plan/latest.json")
P95_DEFAULT_PATH = Path("out/research_fold_drop_spec_builder/latest.json")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build P96 research fold validation plan packet."
    )
    parser.add_argument(
        "--p95-path",
        default=str(P95_DEFAULT_PATH),
        help=(
            "Path to the upstream P95 research_fold_drop_spec_builder packet "
            "(default: %(default)s)."
        ),
    )
    return parser.parse_args(argv)


def _load_p95_packet(path: str | Path) -> dict[str, object] | None:
    """Return parsed JSON dict from *path*, or None if missing or malformed."""
    p = Path(path)
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if not isinstance(data, dict):
        return None
    return data


def run(
    *,
    p95_packet: dict[str, object] | None = None,
    repo_root: str | Path = ROOT,
    out_path: str | Path | None = None,
) -> dict[str, object]:
    return run_packet_and_write(
        repo_root=repo_root,
        out_path=out_path,
        relative_out_path=OUT_PATH,
        build_packet=lambda **_: build_research_fold_validation_plan(
            p95_packet=p95_packet,
        ),
        write_packet=write_research_fold_validation_plan,
    )


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    p95_packet = _load_p95_packet(args.p95_path)
    packet = run(p95_packet=p95_packet)
    print_packet_fields(
        packet,
        "validation_plan_status",
        "recommended_next_lane",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
