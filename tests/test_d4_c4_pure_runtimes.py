"""WP-D4-C4: review/human/proposal/yggdrasil cores have no write helpers."""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

MODULES = [
    "core/review_continuity/runtime.py",
    "core/review_resolution/runtime.py",
    "core/human_decision_continuity/runtime.py",
    "core/proposal_decision_bridge/runtime.py",
    "core/runtime/graph_runner.py",
]


def test_d4_c4_modules_have_no_write_calls() -> None:
    for rel in MODULES:
        text = (REPO / rel).read_text(encoding="utf-8")
        assert "write_canonical_json(" not in text, rel
