from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.research_fold_drop_spec_builder import (  # noqa: E402
    build_research_fold_drop_spec_builder,
    write_research_fold_drop_spec_builder,
)
from scripts.common.runner import print_packet_fields, run_packet_and_write  # noqa: E402

OUT_PATH = Path("out/research_fold_drop_spec_builder/latest.json")
P94_DEFAULT_PATH = Path("out/research_fold_canon_alignment_plan/latest.json")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build P95 research fold drop spec builder packet.")
    parser.add_argument(
        "--p94-path",
        default=str(P94_DEFAULT_PATH),
        help="Path to upstream P94 packet (default: %(default)s).",
    )
    return parser.parse_args(argv)


def _load_p94_packet(path: str | Path) -> dict[str, Any] | None:
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


def run(*, p94_packet: dict[str, Any] | None = None, repo_root: str | Path = ROOT, out_path: str | Path | None = None) -> dict[str, object]:
    return run_packet_and_write(
        repo_root=repo_root,
        out_path=out_path,
        relative_out_path=OUT_PATH,
        build_packet=lambda **_: build_research_fold_drop_spec_builder(p94_packet=p94_packet),
        write_packet=write_research_fold_drop_spec_builder,
    )


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    packet = run(p94_packet=_load_p94_packet(args.p94_path))
    print_packet_fields(packet, "spec_builder_status", "recommended_next_lane")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
