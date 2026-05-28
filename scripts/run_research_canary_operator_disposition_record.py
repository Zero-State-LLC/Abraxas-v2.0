from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.research_canary_operator_disposition_record import (  # noqa: E402
    build_research_canary_operator_disposition_record,
    write_research_canary_operator_disposition_record,
)
from scripts.common.runner import print_packet_fields, run_packet_and_write  # noqa: E402

OUT_PATH = Path("out/research_canary_operator_disposition_record/latest.json")
HOLD_DEFAULT_PATH = Path(
    "out/research_canary_final_activation_authorization_review_hold/latest.json"
)
OBS_DEFAULT_PATH = Path("input/research_canary_operator_disposition_observations.json")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build RESEARCH_CANARY_OPERATOR_DISPOSITION_RECORD advisory artifact."
    )
    parser.add_argument(
        "--hold-path",
        default=str(HOLD_DEFAULT_PATH),
        help="Path to upstream P130 hold artifact (default: %(default)s).",
    )
    parser.add_argument(
        "--observations-path",
        default=str(OBS_DEFAULT_PATH),
        help="Path to operator disposition observations file (default: %(default)s).",
    )
    return parser.parse_args(argv)


def _load_json(path: str | Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    p = Path(path)
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return data if isinstance(data, dict) else None


def run(
    *,
    hold_packet: dict[str, Any] | None = None,
    observations: dict[str, Any] | None = None,
    repo_root: str | Path = ROOT,
    out_path: str | Path | None = None,
) -> dict[str, object]:
    return run_packet_and_write(
        repo_root=repo_root,
        out_path=out_path,
        relative_out_path=OUT_PATH,
        build_packet=lambda **_: build_research_canary_operator_disposition_record(
            hold_packet=hold_packet,
            observations=observations,
        ),
        write_packet=write_research_canary_operator_disposition_record,
    )


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    hold_packet = _load_json(args.hold_path)
    observations = _load_json(args.observations_path)
    packet = run(hold_packet=hold_packet, observations=observations)
    print_packet_fields(packet, "status", "lane_status", "b002_status", "recommended_next_lane")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
