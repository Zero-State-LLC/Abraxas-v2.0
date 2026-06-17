from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.abx_codegen_intelligence_spine_failure_taxonomy_plan import (  # noqa: E402
    build_abx_codegen_intelligence_spine_failure_taxonomy_plan,
    write_abx_codegen_intelligence_spine_failure_taxonomy_plan,
    write_abx_codegen_intelligence_spine_failure_taxonomy_plan_markdown,
)

OUT_JSON = Path("out/audit/abx_codegen_intelligence_spine_failure_taxonomy_plan_001.latest.json")  # noqa: E501
OUT_MD = OUT_JSON.with_suffix(".md")


def run(
    *,
    repo_root: str | Path = ROOT,
    out_json: str | Path | None = None,
    out_md: str | Path | None = None,
) -> dict:
    root = Path(repo_root)
    packet = build_abx_codegen_intelligence_spine_failure_taxonomy_plan(repo_root=root)
    json_target = root / (Path(out_json) if out_json is not None else OUT_JSON)
    md_target = root / (Path(out_md) if out_md is not None else OUT_MD)
    write_abx_codegen_intelligence_spine_failure_taxonomy_plan(json_target, packet)
    write_abx_codegen_intelligence_spine_failure_taxonomy_plan_markdown(md_target, packet)
    return packet


def main() -> int:
    packet = run()
    print(packet["plan_id"])
    print(packet["failure_taxonomy_plan_status"])
    print(packet["recommended_next_lane"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
