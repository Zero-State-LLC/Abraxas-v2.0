from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.research_shadow_stabilization_proof_plan import (  # noqa: E402
    build_research_shadow_stabilization_proof_plan,
    write_research_shadow_stabilization_proof_plan,
)
from scripts.common.runner import print_packet_fields, run_packet_and_write  # noqa: E402

OUT_PATH = Path("out/research_shadow_stabilization_proof_plan/latest.json")
P97_DEFAULT_PATH = Path("out/research_derived_subsystem_candidate_ledger/latest.json")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build P98 research shadow stabilization proof plan packet."
    )
    parser.add_argument(
        "--p97-path",
        default=str(P97_DEFAULT_PATH),
        help=(
            "Path to the upstream P97 research_derived_subsystem_candidate_ledger packet "
            "(default: %(default)s)."
        ),
    )
    return parser.parse_args(argv)


def _load_p97_packet(path: str | Path) -> dict[str, object] | None:
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
    p97_packet: dict[str, object] | None = None,
    repo_root: str | Path = ROOT,
    out_path: str | Path | None = None,
) -> dict[str, object]:
    return run_packet_and_write(
        repo_root=repo_root,
        out_path=out_path,
        relative_out_path=OUT_PATH,
        build_packet=lambda **_: build_research_shadow_stabilization_proof_plan(
            p97_packet=p97_packet,
        ),
        write_packet=write_research_shadow_stabilization_proof_plan,
    )


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    p97_packet = _load_p97_packet(args.p97_path)
    packet = run(p97_packet=p97_packet)
    print_packet_fields(
        packet,
        "stabilization_proof_plan_status",
        "recommended_next_lane",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
