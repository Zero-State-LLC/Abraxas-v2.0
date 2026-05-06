from __future__ import annotations

import json
from pathlib import Path

from core.forecast.runtime import run_forecast_candidates


def main() -> None:
    oracle = json.loads(Path("out/oracle/latest.json").read_text(encoding="utf-8"))
    sandbox = json.loads(Path("out/sandbox/latest.json").read_text(encoding="utf-8"))
    observability = json.loads(Path("out/run_observability_pipeline/latest.json").read_text(encoding="utf-8"))
    run_forecast_candidates(oracle, sandbox, observability)
    print("forecast candidate artifacts emitted")


if __name__ == "__main__":
    main()
