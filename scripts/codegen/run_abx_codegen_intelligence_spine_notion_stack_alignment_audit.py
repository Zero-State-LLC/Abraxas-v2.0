from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.abx_codegen_intelligence_spine_notion_stack_alignment_audit import (  # noqa: E402
    build_abx_codegen_intelligence_spine_notion_stack_alignment_audit,
    write_abx_codegen_intelligence_spine_notion_stack_alignment_audit,
    write_abx_codegen_intelligence_spine_notion_stack_alignment_audit_markdown,
)

OUT_JSON = Path("out/audit/abx_codegen_intelligence_spine_notion_stack_alignment_audit_001.latest.json")  # noqa: E501
OUT_MD = Path("out/audit/abx_codegen_intelligence_spine_notion_stack_alignment_audit_001.latest.md")  # noqa: E501


def run(
    *,
    repo_root: str | Path = ROOT,
    out_json: str | Path | None = None,
    out_md: str | Path | None = None,
) -> dict:
    root = Path(repo_root)
    packet = build_abx_codegen_intelligence_spine_notion_stack_alignment_audit(
        repo_root=root
    )
    json_target = root / (Path(out_json) if out_json is not None else OUT_JSON)
    md_target = root / (Path(out_md) if out_md is not None else OUT_MD)
    write_abx_codegen_intelligence_spine_notion_stack_alignment_audit(
        json_target, packet
    )
    write_abx_codegen_intelligence_spine_notion_stack_alignment_audit_markdown(
        md_target, packet
    )
    return packet


def main() -> int:
    packet = run()
    print(packet["audit_id"])
    print(packet["audit_status"])
    print(packet["recommended_next_lane"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
