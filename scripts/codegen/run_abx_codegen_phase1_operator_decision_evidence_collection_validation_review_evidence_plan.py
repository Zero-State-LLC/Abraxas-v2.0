from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_plan import (  # noqa: E402
    write_abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_plan,
)

OUT_JSON = Path("out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_plan_001.latest.json")  # noqa: E501
OUT_MD = OUT_JSON.with_suffix(".md")


def run(
    *,
    repo_root: str | Path = ROOT,
    out_root: str | Path | None = None,
) -> dict[str, object]:
    return write_abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_plan(
        repo_root,
        out_root=out_root,
    )


def main() -> int:
    packet = run()
    print(packet["status"])
    print(packet["recommended_next_patch"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
