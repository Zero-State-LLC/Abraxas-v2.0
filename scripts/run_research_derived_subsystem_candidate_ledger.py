from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.research_derived_subsystem_candidate_ledger import (  # noqa: E402
    build_research_derived_subsystem_candidate_ledger,
    write_research_derived_subsystem_candidate_ledger,
)
from scripts.common.runner import print_packet_fields, run_packet_and_write  # noqa: E402

OUT_PATH = Path("out/research_derived_subsystem_candidate_ledger/latest.json")
P96_DEFAULT_PATH = Path("out/research_fold_validation_plan/latest.json")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build P97 research-derived subsystem candidate ledger packet."
    )
    parser.add_argument(
        "--p96-path",
        default=str(P96_DEFAULT_PATH),
        help=(
            "Path to the upstream P96 research_fold_validation_plan packet "
            "(default: %(default)s)."
        ),
    )
    return parser.parse_args(argv)


def _load_p96_packet(path: str | Path) -> dict[str, object] | None:
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
    p96_packet: dict[str, object] | None = None,
    repo_root: str | Path = ROOT,
    out_path: str | Path | None = None,
) -> dict[str, object]:
    return run_packet_and_write(
        repo_root=repo_root,
        out_path=out_path,
        relative_out_path=OUT_PATH,
        build_packet=lambda **_: build_research_derived_subsystem_candidate_ledger(
            p96_packet=p96_packet,
        ),
        write_packet=write_research_derived_subsystem_candidate_ledger,
    )


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    p96_packet = _load_p96_packet(args.p96_path)
    packet = run(p96_packet=p96_packet)
    print_packet_fields(
        packet,
        "status",
        "recommended_next_lane",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
