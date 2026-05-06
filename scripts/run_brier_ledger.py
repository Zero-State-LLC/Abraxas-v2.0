from __future__ import annotations

import json
from pathlib import Path

from core.brier.runtime import run_brier_ledger


def main() -> None:
    forecast = json.loads(Path("out/forecast/latest.json").read_text(encoding="utf-8"))
    outcome = forecast["outcome_binding"]
    run_brier_ledger(forecast, outcome)
    print("brier ledger artifacts emitted")


if __name__ == "__main__":
    main()
