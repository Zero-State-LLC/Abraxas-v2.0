from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.sync.v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_intake_gate import (  # noqa: E402
    GATE_JSON_PATH,
    write_v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_intake_gate,
)

OUT_JSON_PATH = Path("out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_intake_gate_001.latest.json")
OUT_MD_PATH = OUT_JSON_PATH.with_suffix(".md")


def run(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    return write_v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_intake_gate(
        repo_root,
        out_root=out_root,
    )


def main() -> None:
    packet = run()
    print(f"wrote {GATE_JSON_PATH}")
    print(f"status={packet['status']}")
    print(f"gate_hash={packet['gate_hash']}")


if __name__ == "__main__":
    main()
