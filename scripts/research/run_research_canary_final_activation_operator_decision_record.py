from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.research_canary_final_activation_operator_decision_record import (  # noqa: E402
    write_research_canary_final_activation_operator_decision_record,
)


def run(repo_root: str | Path = ".", out_path: Path | None = None) -> dict:
    return write_research_canary_final_activation_operator_decision_record(
        repo_root, out_path=out_path
    )


if __name__ == "__main__":
    packet = run()
    print(packet["lane_id"])
    print(packet["status"])
    print(packet["recommended_next_lane"])
