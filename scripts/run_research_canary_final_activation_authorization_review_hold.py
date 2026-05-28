from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.research_canary_final_activation_authorization_review_hold import (  # noqa: E402
    build_research_canary_final_activation_authorization_review_hold,
    write_research_canary_final_activation_authorization_review_hold,
)
from scripts.common.runner import print_packet_fields, run_packet_and_write  # noqa: E402

OUT_PATH = Path("out/research_canary_final_activation_authorization_review_hold/latest.json")
P130_DEFAULT_PATH = Path("out/research_canary_final_activation_authorization_review/latest.json")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build P130_HOLD research canary final activation authorization review hold record."
    )
    parser.add_argument(
        "--p130-path",
        default=str(P130_DEFAULT_PATH),
        help="Path to upstream P130 packet (default: %(default)s).",
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
    return data if isinstance(data, dict) else None


def run(
    *,
    p130_packet: dict[str, Any] | None = None,
    repo_root: str | Path = ROOT,
    out_path: str | Path | None = None,
) -> dict[str, object]:
    return run_packet_and_write(
        repo_root=repo_root,
        out_path=out_path,
        relative_out_path=OUT_PATH,
        build_packet=lambda **_: build_research_canary_final_activation_authorization_review_hold(
            p130_packet=p130_packet
        ),
        write_packet=write_research_canary_final_activation_authorization_review_hold,
    )


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    packet = run(p130_packet=_load_json_packet(args.p130_path))
    print_packet_fields(packet, "status", "lane_status", "recommended_next_lane")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
