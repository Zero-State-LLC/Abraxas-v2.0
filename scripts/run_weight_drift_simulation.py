from __future__ import annotations

import json
from pathlib import Path

from core.drift.runtime import run_weight_drift_simulation


def main() -> None:
    reliability = json.loads(Path("out/brier_reliability/latest.json").read_text(encoding="utf-8"))
    brier = json.loads(Path("out/brier/latest.json").read_text(encoding="utf-8"))
    forecast = json.loads(Path("out/forecast/latest.json").read_text(encoding="utf-8"))
    run_weight_drift_simulation(reliability, brier, forecast)
    print("drift artifacts emitted")


if __name__ == "__main__":
    main()
