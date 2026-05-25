from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.research_canary_eligibility_dossier import (  # noqa: E402
    build_research_canary_eligibility_dossier,
    write_research_canary_eligibility_dossier,
)
from scripts.common.runner import print_packet_fields, run_packet_and_write  # noqa: E402

OUT_PATH = Path("out/research_canary_eligibility_dossier/latest.json")
P105_DEFAULT_PATH = Path("out/research_promotion_blocker_ledger/latest.json")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build P106 research canary eligibility dossier packet."
    )
    parser.add_argument(
        "--p105-path",
        default=str(P105_DEFAULT_PATH),
        help=(
            "Path to upstream P105 research_promotion_blocker_ledger packet "
            "(default: %(default)s)."
        ),
    )
    parser.add_argument(
        "--eligibility-observations-path",
        default=None,
        help=(
            "Optional path to per-candidate eligibility observations for "
            "blocker-review-complete candidates."
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
    p105_packet: dict[str, Any] | None = None,
    eligibility_observations_packet: dict[str, Any] | None = None,
    repo_root: str | Path = ROOT,
    out_path: str | Path | None = None,
) -> dict[str, object]:
    return run_packet_and_write(
        repo_root=repo_root,
        out_path=out_path,
        relative_out_path=OUT_PATH,
        build_packet=lambda **_: build_research_canary_eligibility_dossier(
            p105_packet=p105_packet,
            eligibility_observations_packet=eligibility_observations_packet,
        ),
        write_packet=write_research_canary_eligibility_dossier,
    )


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    p105_packet = _load_json_packet(args.p105_path)
    eligibility_observations_packet = _load_json_packet(
        args.eligibility_observations_path
    )
    packet = run(
        p105_packet=p105_packet,
        eligibility_observations_packet=eligibility_observations_packet,
    )
    print_packet_fields(
        packet,
        "status",
        "canary_eligibility_dossier_status",
        "recommended_next_lane",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
