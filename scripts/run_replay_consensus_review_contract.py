from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.replay_consensus.review import write_replay_consensus_review_contract_audit

OUT_PATH = Path("out/audit/replay_consensus_review_contract.latest.json")


def main() -> None:
    write_replay_consensus_review_contract_audit(".")
    if not OUT_PATH.exists():
        raise FileNotFoundError(OUT_PATH)


if __name__ == "__main__":
    main()
