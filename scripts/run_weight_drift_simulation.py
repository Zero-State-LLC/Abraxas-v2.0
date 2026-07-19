from __future__ import annotations

import json
from pathlib import Path

from core.canonical.json import write_canonical_json
from core.drift.runtime import build_weight_drift_simulation


def main() -> None:
    reliability = json.loads(
        Path("out/brier_reliability/latest.json").read_text(encoding="utf-8")
    )
    brier = json.loads(Path("out/brier/latest.json").read_text(encoding="utf-8"))
    forecast = json.loads(Path("out/forecast/latest.json").read_text(encoding="utf-8"))
    out = build_weight_drift_simulation(reliability, brier, forecast)
    write_canonical_json(Path("out/drift/latest.json"), out)
    write_canonical_json(Path("out/drift_lineage/latest.json"), out["lineage"])
    write_canonical_json(Path("out/drift_reliability/latest.json"), out["reliability"])
    write_canonical_json(Path("out/drift_replay/latest.json"), out["replay"])
    print("drift artifacts emitted")


if __name__ == "__main__":
    main()
