from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.sync.oracle_signal_intake_boundary_implementation_plan import (  # noqa: E402
    OUT_JSON,
    OUT_MD,
    build_oracle_signal_intake_boundary_implementation_plan,
    write_oracle_signal_intake_boundary_implementation_plan,
    write_oracle_signal_intake_boundary_implementation_plan_markdown,
)


def run(
    *,
    repo_root: str | Path = ROOT,
    out_json: str | Path | None = None,
    out_md: str | Path | None = None,
) -> dict:
    root = Path(repo_root)
    packet = build_oracle_signal_intake_boundary_implementation_plan(repo_root=root)
    json_target = root / (Path(out_json) if out_json is not None else Path(OUT_JSON))
    md_target = root / (Path(out_md) if out_md is not None else Path(OUT_MD))
    write_oracle_signal_intake_boundary_implementation_plan(json_target, packet)
    write_oracle_signal_intake_boundary_implementation_plan_markdown(md_target, packet)
    return packet


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.parse_args()
    packet = run()
    print(packet["plan_id"])
    print(packet["plan_status"])
    print(packet["recommended_next_patch"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
