from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.global_operator_review_queue import write_global_operator_review_queue_artifacts  # noqa: E402


def main() -> int:
    artifacts = write_global_operator_review_queue_artifacts()
    print(artifacts["queue_run"]["status"])
    print(artifacts["queue_run"]["run_id"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
