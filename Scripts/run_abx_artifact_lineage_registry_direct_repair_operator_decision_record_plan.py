from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.abx_artifact_lineage_registry_direct_repair_operator_decision_record_plan import (  # noqa: E402
    write_abx_artifact_lineage_registry_direct_repair_operator_decision_record_plan,
)


def run(*, repo_root: str | Path = ROOT):
    return write_abx_artifact_lineage_registry_direct_repair_operator_decision_record_plan(repo_root)


def main() -> int:
    packet = run()
    print(json.dumps({"decision_record_plan_id": packet["decision_record_plan_id"], "status": packet["status"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
