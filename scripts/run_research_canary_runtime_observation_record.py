from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.research_canary_runtime_observation_record import (  # noqa: E402
    build_research_canary_runtime_observation_record,
    write_research_canary_runtime_observation_record,
)
from scripts.common.runner import print_packet_fields, run_packet_and_write  # noqa: E402

OUT_PATH = Path("out/research_canary_runtime_observation_record/latest.json")
P118_DEFAULT_PATH = Path("out/research_controlled_canary_envelope_draft/latest.json")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build P119 research canary runtime observation record."
    )
    parser.add_argument(
        "--p118-path",
        default=str(P118_DEFAULT_PATH),
        help=(
            "Path to upstream P118 research_controlled_canary_envelope_draft packet "
            "(default: %(default)s)."
        ),
    )
    parser.add_argument(
        "--runtime-observation-evidence-path",
        default=None,
        help=(
            "Optional path to per-candidate runtime observation evidence for "
            "envelope-draft-complete candidates in P118."
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
    p118_packet: dict[str, Any] | None = None,
    runtime_observation_evidence_packet: dict[str, Any] | None = None,
    repo_root: str | Path = ROOT,
    out_path: str | Path | None = None,
) -> dict[str, object]:
    return run_packet_and_write(
        repo_root=repo_root,
        out_path=out_path,
        relative_out_path=OUT_PATH,
        build_packet=lambda **_: build_research_canary_runtime_observation_record(
            p118_packet=p118_packet,
            runtime_observation_evidence_packet=runtime_observation_evidence_packet,
        ),
        write_packet=write_research_canary_runtime_observation_record,
    )


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    p118_packet = _load_json_packet(args.p118_path)
    runtime_observation_evidence_packet = _load_json_packet(
        args.runtime_observation_evidence_path
    )
    packet = run(
        p118_packet=p118_packet,
        runtime_observation_evidence_packet=runtime_observation_evidence_packet,
    )
    print_packet_fields(packet, "status", "lane_status", "recommended_next_lane")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
