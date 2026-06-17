from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.sync.v2_hygiene_phase1_authorization_record_review_evidence_dry_run_review import (  # noqa: E402
    write_v2_hygiene_phase1_authorization_record_review_evidence_dry_run_review,
)

OUT_JSON = Path("out/operator_review/v2_hygiene_phase1_authorization_record_review_evidence_dry_run_review_001.latest.json")
OUT_MD = OUT_JSON.with_suffix(".md")


def run(*, repo_root: str | Path = ROOT, out_root: str | Path | None = None) -> dict[str, object]:
    return write_v2_hygiene_phase1_authorization_record_review_evidence_dry_run_review(
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
