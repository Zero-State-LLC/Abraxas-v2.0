from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.abx_artifact_lineage_runner_casing_policy_review_request import (  # noqa: E402
    write_abx_artifact_lineage_runner_casing_policy_review_request,
)


def run(*, repo_root: str | Path = ROOT):
    return write_abx_artifact_lineage_runner_casing_policy_review_request(repo_root)


def main() -> int:
    packet = run()
    print(
        json.dumps(
            {
                "request_hash": packet["request_hash"],
                "status": packet["status"],
                "recommended_next_lane": packet["recommended_next_lane"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
