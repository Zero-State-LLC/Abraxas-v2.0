from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.abx_harness_implementation_authorization_intake_gate import (  # noqa: E402
    DEFAULT_PAYLOAD_PATH,
    build_abx_harness_implementation_authorization_intake_gate,
)

REQUIRED_FIELDS = (
    "record_type",
    "record_id",
    "decision_value",
    "status",
    "implementation_scope",
    "authority_boundaries",
    "operator_acknowledgements",
    "seal",
)


def run(repo_root: str | Path = ROOT) -> int:
    root = Path(repo_root)
    payload_path = root / DEFAULT_PAYLOAD_PATH
    if not payload_path.is_file():
        print(f"FAIL: payload missing at {payload_path}")
        return 1

    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    missing = [field for field in REQUIRED_FIELDS if field not in payload]
    if missing:
        print(f"FAIL: missing fields: {', '.join(missing)}")
        return 1

    gate = build_abx_harness_implementation_authorization_intake_gate(root)
    if gate["intake_validated_for_authorization_record"]:
        print("PASS: harness implementation authorization payload preflight")
        return 0

    print(f"FAIL: validation blockers: {gate['validation_blockers']}")
    return 1


if __name__ == "__main__":
    raise SystemExit(run())
