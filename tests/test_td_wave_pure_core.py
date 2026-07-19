"""TD Wave 1: remaining core modules pure (no out/ publication)."""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

MODULES = [
    "core/runtime/topology_replay.py",
    "core/spine/milestone_continuity.py",
    "core/abraxas_oracle_execution_boundary.py",
    "core/abraxas_oracle_pre_execution_snapshot.py",
    "core/research_canary_final_activation_authorization_review.py",
]


def test_td_wave1_core_has_no_out_write_calls() -> None:
    for rel in MODULES:
        text = (REPO / rel).read_text(encoding="utf-8")
        assert "write_canonical_json(" not in text, rel
        # No direct filesystem writes to out/
        for line in text.splitlines():
            if "write_text" in line and "out/" in line:
                raise AssertionError(f"{rel}: {line}")
            if "write_bytes" in line and "out/" in line:
                raise AssertionError(f"{rel}: {line}")
