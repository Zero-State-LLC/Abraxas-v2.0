from __future__ import annotations

import json
from pathlib import Path


def test_projection_invariants() -> None:
    packet = json.loads(Path("out/projections/aal_viz.latest.json").read_text())
    assert packet["projection_only"] is True
    assert packet["inference_authority"] is False
