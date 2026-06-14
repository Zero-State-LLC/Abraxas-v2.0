from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.sync.v2_hygiene_loop_awareness_operator_authorization_gate import (  # noqa: E402
    build_v2_hygiene_loop_awareness_operator_authorization_gate,
    write_v2_hygiene_loop_awareness_operator_authorization_gate,
    write_v2_hygiene_loop_awareness_operator_authorization_gate_markdown,
)

OUT_JSON = Path("out/operator_review/v2_hygiene_loop_awareness_operator_authorization_gate_001.latest.json")
OUT_MD = OUT_JSON.with_suffix(".md")


def run(
    *,
    repo_root: str | Path = ROOT,
    out_json: str | Path | None = None,
    out_md: str | Path | None = None,
) -> dict:
    root = Path(repo_root)
    packet = build_v2_hygiene_loop_awareness_operator_authorization_gate(root)
    json_target = root / (Path(out_json) if out_json is not None else OUT_JSON)
    md_target = root / (Path(out_md) if out_md is not None else OUT_MD)
    write_v2_hygiene_loop_awareness_operator_authorization_gate(json_target, packet)
    write_v2_hygiene_loop_awareness_operator_authorization_gate_markdown(md_target, packet)
    return packet


def main() -> int:
    packet = run()
    print(packet["gate_id"])
    print(packet["gate_status"])
    print(packet["recommended_next_patch"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
