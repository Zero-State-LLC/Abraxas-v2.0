# ruff: noqa: E402

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.global_pipeline_repo_execution_prep import write_global_pipeline_repo_execution_prep_artifacts


def main() -> int:
    artifacts = write_global_pipeline_repo_execution_prep_artifacts()
    print(artifacts["prep_packet"]["status"])
    print(artifacts["prep_packet"]["prep_packet_id"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
