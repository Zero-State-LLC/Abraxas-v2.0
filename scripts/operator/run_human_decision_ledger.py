from __future__ import annotations

from core.canonical.json import write_canonical_json
from core.human_decision_ledger.runtime import run_human_decision_ledger


if __name__ == "__main__":
    packet = run_human_decision_ledger([], [], [], [])
    write_canonical_json("out/human_decision_ledger/latest.json", packet)
    write_canonical_json(
        "out/human_decision_ledger_replay/latest.json", packet["replay"]
    )
    write_canonical_json(
        "out/human_decision_ledger_lineage/latest.json", packet["lineage"]
    )
    write_canonical_json(
        "out/human_decision_ledger_diagnostics/latest.json", packet["diagnostics"]
    )
