from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.sync.p102g_plus_operator_decision_surface_audit import (  # noqa: E402
    build_p102g_plus_operator_decision_surface_audit,
    write_p102g_plus_operator_decision_surface_audit,
    write_p102g_plus_operator_decision_surface_audit_markdown,
)

OUT_JSON = Path("out/operator_review/p102g_plus_operator_decision_surface_audit_001.latest.json")
OUT_MD = OUT_JSON.with_suffix(".md")


def run(
    *,
    repo_root: str | Path = ROOT,
    out_json: str | Path | None = None,
    out_md: str | Path | None = None,
) -> dict:
    root = Path(repo_root)
    packet = build_p102g_plus_operator_decision_surface_audit(root)
    json_target = root / (Path(out_json) if out_json is not None else Path(OUT_JSON))
    md_target = root / (Path(out_md) if out_md is not None else Path(OUT_MD))
    write_p102g_plus_operator_decision_surface_audit(json_target, packet)
    write_p102g_plus_operator_decision_surface_audit_markdown(md_target, packet)
    return packet


def main() -> int:
    packet = run()
    print(packet["audit_id"])
    print(packet["audit_status"])
    print(packet["recommended_next_patch"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
