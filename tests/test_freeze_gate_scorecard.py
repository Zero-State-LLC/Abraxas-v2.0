"""Tests for WP-GATE freeze scorecard."""

from __future__ import annotations

from pathlib import Path

from core.production_readiness.freeze_gate_scorecard import build_freeze_gate_scorecard


REPO = Path(__file__).resolve().parents[1]


def test_scorecard_has_eight_gates() -> None:
    card = build_freeze_gate_scorecard(REPO, write=False)
    assert card["schema_version"] == "freeze_gate_scorecard.v1"
    assert len(card["gates"]) == 8
    ids = {g["gate_id"] for g in card["gates"]}
    assert ids == {"G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8"}
    assert card["summary"]["gate_count"] == 8
