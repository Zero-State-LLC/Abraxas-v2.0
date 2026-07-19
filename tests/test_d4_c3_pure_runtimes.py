"""WP-D4-C3: observability / sandbox / firewall cores have no write helpers."""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

MODULES = [
    "core/observability/aggregation.py",
    "core/proposal_sandbox_routing/runtime.py",
    "core/proposal_sandbox_evaluation/runtime.py",
    "core/overlay_firewall/runtime.py",
]


def test_d4_c3_modules_have_no_write_calls() -> None:
    for rel in MODULES:
        text = (REPO / rel).read_text(encoding="utf-8")
        assert "write_canonical_json(" not in text, rel
        assert "from core.canonical.json import write_canonical_json" not in text, rel
