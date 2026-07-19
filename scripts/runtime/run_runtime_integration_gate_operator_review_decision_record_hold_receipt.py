from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.runtime_integration_gate_operator_review_decision_record import (  # noqa: E402
    write_runtime_integration_gate_operator_review_decision_record,
)
from core.runtime_integration_gate_operator_review_decision_record_hold_receipt import (  # noqa: E402
    RECEIPT_JSON_PATH,
    write_runtime_integration_gate_operator_review_decision_record_hold_receipt,
)
from core.runtime_integration_gate_operator_review_decision_record_plan import (  # noqa: E402
    write_runtime_integration_gate_operator_review_decision_record_plan,
)


def run(repo_root: str | Path = ".", *, out_root: str | Path | None = None):
    write_runtime_integration_gate_operator_review_decision_record_plan(
        repo_root, out_root=out_root
    )
    write_runtime_integration_gate_operator_review_decision_record(
        repo_root, out_root=out_root
    )
    return write_runtime_integration_gate_operator_review_decision_record_hold_receipt(
        repo_root, out_root=out_root
    )


def main() -> None:
    packet = run()
    print(f"wrote {RECEIPT_JSON_PATH}")
    print(f"status={packet['status']}")


if __name__ == "__main__":
    main()
