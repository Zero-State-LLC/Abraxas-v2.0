from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.canonical.json import write_canonical_json  # noqa: E402
from core.research_canary_final_activation_authorization_review import (  # noqa: E402
    build_research_canary_final_activation_authorization_review,
)
from scripts.common.runner import print_packet_fields, run_packet_and_write  # noqa: E402

OUT_PATH = Path("out/research_canary_final_activation_authorization_review/latest.json")
P129_DEFAULT_PATH = Path("out/research_canary_activation_readiness_evidence_record/latest.json")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build P130 research canary final activation authorization review.")
    parser.add_argument(
        "--p129-path",
        default=str(P129_DEFAULT_PATH),
        help="Path to upstream P129 packet (default: %(default)s).",
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


def run(*, p129_packet: dict[str, Any] | None = None, repo_root: str | Path = ROOT, out_path: str | Path | None = None) -> dict[str, object]:
    return run_packet_and_write(
        repo_root=repo_root,
        out_path=out_path,
        relative_out_path=OUT_PATH,
        build_packet=lambda **_: build_research_canary_final_activation_authorization_review(p129_packet=p129_packet),
        write_packet=write_canonical_json,
    )


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    packet = run(p129_packet=_load_json_packet(args.p129_path))
    print_packet_fields(packet, "status", "lane_status", "recommended_next_lane")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
