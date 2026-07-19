from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.sync.v2_hygiene_phase1_operator_review_stabilization_operator_decision_record import (  # noqa: E402
    RECORD_JSON_PATH,
    write_v2_hygiene_phase1_operator_review_stabilization_operator_decision_record,
)


def run(repo_root: str | Path = ".", *, out_root: str | Path | None = None):
    return write_v2_hygiene_phase1_operator_review_stabilization_operator_decision_record(
        repo_root, out_root=out_root
    )


def main() -> None:
    packet = run()
    print(f"wrote {RECORD_JSON_PATH}")
    print(f"status={packet['status']}")


if __name__ == "__main__":
    main()
