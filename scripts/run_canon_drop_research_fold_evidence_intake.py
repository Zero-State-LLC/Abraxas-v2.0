from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.canon_drop_research_fold_evidence_intake import (  # noqa: E402
    build_canon_drop_research_fold_evidence_intake,
    write_canon_drop_research_fold_evidence_intake,
)
from scripts.common.runner import print_packet_fields, run_packet_and_write  # noqa: E402

OUT_PATH = Path("out/canon_drop_research_fold_evidence_intake/latest.json")
DEFAULT_MANIFEST_PATH = Path("input/canon_drop_research_fold_evidence_manifest.json")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build P093 canon drop research fold evidence intake packet.")
    parser.add_argument(
        "--manifest-path",
        default=str(DEFAULT_MANIFEST_PATH),
        help="Path to canon drop research fold evidence manifest (default: %(default)s).",
    )
    return parser.parse_args(argv)


def _load_json_packet(path: str | Path) -> dict[str, Any] | None:
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
    manifest: dict[str, Any] | None = None,
    repo_root: str | Path = ROOT,
    out_path: str | Path | None = None,
) -> dict[str, object]:
    return run_packet_and_write(
        repo_root=repo_root,
        out_path=out_path,
        relative_out_path=OUT_PATH,
        build_packet=lambda **_: build_canon_drop_research_fold_evidence_intake(
            manifest=manifest
        ),
        write_packet=write_canon_drop_research_fold_evidence_intake,
    )


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    manifest = _load_json_packet(args.manifest_path)
    packet = run(manifest=manifest)
    print_packet_fields(packet, "intake_status", "evidence_complete", "recommended_next_lane")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
