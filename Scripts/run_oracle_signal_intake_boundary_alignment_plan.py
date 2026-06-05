from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.sync.global_ingest_adapter_spine_alignment_plan import (  # noqa: E402
    OUT_JSON as GLOBAL_INGEST_ALIGNMENT_JSON,
)
from core.sync.oracle_signal_intake_boundary_alignment_plan import (  # noqa: E402
    OUT_JSON,
    OUT_MD,
    build_oracle_signal_intake_boundary_alignment_plan,
    write_oracle_signal_intake_boundary_alignment_plan,
    write_oracle_signal_intake_boundary_alignment_plan_markdown,
)


def run(
    *,
    repo_root: str | Path = ROOT,
    out_json: str | Path | None = None,
    out_md: str | Path | None = None,
    global_ingest_alignment_path: str | Path = GLOBAL_INGEST_ALIGNMENT_JSON,
) -> dict:
    root = Path(repo_root)
    packet = build_oracle_signal_intake_boundary_alignment_plan(
        repo_root=root,
        global_ingest_alignment_path=global_ingest_alignment_path,
    )
    json_target = root / (Path(out_json) if out_json is not None else Path(OUT_JSON))
    md_target = root / (Path(out_md) if out_md is not None else Path(OUT_MD))
    write_oracle_signal_intake_boundary_alignment_plan(json_target, packet)
    write_oracle_signal_intake_boundary_alignment_plan_markdown(md_target, packet)
    return packet


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--global-ingest-alignment", default=GLOBAL_INGEST_ALIGNMENT_JSON)
    args = parser.parse_args()
    packet = run(global_ingest_alignment_path=args.global_ingest_alignment)
    print(packet["plan_id"])
    print(packet["plan_status"])
    print(packet["recommended_next_patch"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
