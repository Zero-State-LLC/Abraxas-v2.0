from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.abx_research_canary_artifact_registry_coverage_repair_operator_decision_record import (  # noqa: E402
    write_abx_research_canary_artifact_registry_coverage_repair_operator_decision_record,
)


def run(*, repo_root: str | Path = ROOT, out_root: str | Path | None = None) -> dict[str, object]:
    return write_abx_research_canary_artifact_registry_coverage_repair_operator_decision_record(
        source_root=repo_root,
        out_root=out_root,
    )


def main() -> int:
    packet = run()
    print(packet["status"])
    print(packet["selected_decision"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
