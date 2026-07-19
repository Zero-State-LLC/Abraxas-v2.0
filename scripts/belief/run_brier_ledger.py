from __future__ import annotations

import json
from pathlib import Path

from core.brier.runtime import build_brier_ledger
from core.canonical.json import write_canonical_json


def main() -> None:
    forecast = json.loads(Path("out/forecast/latest.json").read_text(encoding="utf-8"))
    outcome = forecast["outcome_binding"]
    out = build_brier_ledger(forecast, outcome)
    write_canonical_json(Path("out/brier/latest.json"), out)
    write_canonical_json(Path("out/brier_lineage/latest.json"), out["lineage"])
    write_canonical_json(Path("out/brier_reliability/latest.json"), out["reliability"])
    write_canonical_json(Path("out/brier_replay/latest.json"), out["replay"])
    print("brier ledger artifacts emitted")


if __name__ == "__main__":
    main()
