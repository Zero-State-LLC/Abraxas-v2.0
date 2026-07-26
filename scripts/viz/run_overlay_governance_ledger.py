from __future__ import annotations

import json
from pathlib import Path

from core.canonical.json import write_canonical_json
from core.overlay_governance.runtime import run_overlay_governance_ledger


def _load(path: str) -> list[dict]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(
            f"required overlay governance upstream missing: {path} "
            "(refuse empty-packet fallback)"
        )
    payload = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"overlay governance upstream must be a JSON object: {path}")
    return [payload]


if __name__ == "__main__":
    packet = run_overlay_governance_ledger(
        _load("out/canary/latest.json"),
        _load("out/overlay_observability/latest.json"),
        _load("out/canary_scheduler/latest.json"),
        _load("out/canary_promotion/latest.json"),
    )
    write_canonical_json("out/overlay_governance/latest.json", packet)
    write_canonical_json("out/overlay_governance_replay/latest.json", packet["replay"])
    write_canonical_json(
        "out/overlay_governance_lineage/latest.json", packet["lineage"]
    )
    write_canonical_json(
        "out/overlay_governance_diagnostics/latest.json", packet["diagnostics"]
    )
